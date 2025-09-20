import os
import json
import time
import logging
import pandas as pd
import numpy as np
from datetime import datetime
import pathway as pw
from pathway.stdlib.ml.index import KNNIndex
from pathway.stdlib.ml.embedders import OpenAIEmbedder
from pathway.stdlib.ml.llms import OpenAILLM
from pathway.stdlib.utils.col import unpack_col

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LogisticsRAGPipeline:
    """Real-time RAG pipeline for logistics data using Pathway."""

    def __init__(self, config):
        """Initialize the RAG pipeline.

        Args:
            config: Configuration dictionary with the following keys:
                - api_key: OpenAI API key
                - data_dirs: Dictionary mapping data types to directories
                - output_dir: Directory to write results
                - model: LLM model to use (default: gpt-3.5-turbo)
                - embedding_model: Embedding model to use (default: text-embedding-ada-002)
                - temperature: LLM temperature (default: 0.0)
        """
        self.config = config
        self.api_key = config.get("api_key")
        self.data_dirs = config.get("data_dirs", {})
        self.output_dir = config.get("output_dir", "./output")
        self.model = config.get("model", "gpt-3.5-turbo")
        self.embedding_model = config.get("embedding_model", "text-embedding-ada-002")
        self.temperature = config.get("temperature", 0.0)
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize Pathway components
        self.pw_context = None
        self.embedder = None
        self.llm = None
        self.data_tables = {}
        self.vector_indexes = {}
        self.query_table = None
        self.response_table = None

    def build_pipeline(self):
        """Build the Pathway RAG pipeline."""
        # Create a Pathway context
        self.pw_context = pw.io.python.run_all()

        # Initialize embedder and LLM
        self.embedder = OpenAIEmbedder(api_key=self.api_key, model=self.embedding_model)
        self.llm = OpenAILLM(api_key=self.api_key, model=self.model, temperature=self.temperature)

        # Create data tables and indexes for each data type
        for data_type, data_dir in self.data_dirs.items():
            if os.path.exists(data_dir):
                self._create_data_table(data_type, data_dir)
            else:
                logger.warning(f"Data directory not found: {data_dir}")

        # Create query input connector
        self.query_table = pw.io.http.rest_connector(
            host="0.0.0.0",
            port=8080,
            endpoint="/query",
            schema=pw.schema_builder().add("query", pw.Type.STRING).add("user_id", pw.Type.STRING).build(),
            autocommit=True,
        )

        # Process queries
        query_with_embedding = self.query_table.select(
            pw.this.query,
            pw.this.user_id,
            embedding=self.embedder.embed(pw.this.query),
            timestamp=pw.apply(lambda: datetime.now().isoformat()),
        )

        # Perform retrieval for each data type
        retrieval_results = {}
        for data_type, index in self.vector_indexes.items():
            if index is not None:
                # Get relevant documents from the index
                retrieval_results[data_type] = index.query(
                    query_with_embedding.embedding,
                    k=5,  # Retrieve top 5 results
                    query_id=query_with_embedding.user_id,
                ).select(
                    pw.this.query_id,
                    data_type=pw.apply(lambda: data_type),
                    document=pw.this.document,
                    score=pw.this.score,
                )

        # Combine retrieval results
        if retrieval_results:
            combined_results = None
            for data_type, result in retrieval_results.items():
                if combined_results is None:
                    combined_results = result
                else:
                    combined_results = combined_results.concat(result)

            # Group results by query_id
            grouped_results = combined_results.groupby(pw.this.query_id).reduce(
                query_id=pw.this.query_id,
                context=pw.apply(
                    self._format_context,
                    pw.this.data_type.collect(),
                    pw.this.document.collect(),
                    pw.this.score.collect(),
                ),
            )

            # Join with original query
            query_with_context = query_with_embedding.join(
                grouped_results,
                query_with_embedding.user_id == grouped_results.query_id,
            ).select(
                pw.this.query,
                pw.this.user_id,
                pw.this.context,
                pw.this.timestamp,
            )

            # Generate response using LLM
            self.response_table = query_with_context.select(
                pw.this.query,
                pw.this.user_id,
                pw.this.timestamp,
                response=self.llm.apply(
                    self._generate_prompt,
                    pw.this.query,
                    pw.this.context,
                ),
            )
        else:
            # Fallback if no indexes are available
            self.response_table = query_with_embedding.select(
                pw.this.query,
                pw.this.user_id,
                pw.this.timestamp,
                response=self.llm.apply(
                    self._generate_fallback_prompt,
                    pw.this.query,
                ),
            )

        # Write responses to output connector
        pw.io.http.rest_connector(
            self.response_table,
            host="0.0.0.0",
            port=8080,
            endpoint="/response/{user_id}",
            autocommit=True,
        )

        # Also write responses to file for logging
        pw.io.fs.write(
            self.response_table,
            os.path.join(self.output_dir, "responses"),
            format="json",
            filename_pattern="response_{timestamp}.json",
        )

        return self

    def _create_data_table(self, data_type, data_dir):
        """Create a data table and vector index for a specific data type.

        Args:
            data_type: Type of data (e.g., 'drivers', 'incidents', 'shipments')
            data_dir: Directory containing the data files
        """
        try:
            # Create input connector for the data directory
            data_table = pw.io.fs.read(
                data_dir,
                format="auto",  # Auto-detect format based on file extension
                mode="streaming",  # Use streaming mode to continuously monitor for new files
                with_metadata=True,
            )

            # Process the data based on its type
            processed_table = data_table.select(
                document=pw.apply(self._process_document, pw.this.data, data_type),
                metadata=pw.this._pw_path_name,
            ).filter(pw.this.document != "")

            # Create embeddings
            embedded_table = processed_table.select(
                pw.this.document,
                pw.this.metadata,
                embedding=self.embedder.embed(pw.this.document),
            )

            # Create vector index
            index = KNNIndex(embedded_table.embedding, embedded_table.document)
            
            # Store table and index references
            self.data_tables[data_type] = embedded_table
            self.vector_indexes[data_type] = index
            
            logger.info(f"Created vector index for {data_type} data")
        except Exception as e:
            logger.error(f"Error creating data table for {data_type}: {e}")
            self.data_tables[data_type] = None
            self.vector_indexes[data_type] = None

    def _process_document(self, data, data_type):
        """Process a document based on its data type.

        Args:
            data: Document data
            data_type: Type of data

        Returns:
            Processed document text
        """
        try:
            if not data:
                return ""
                
            # Convert to dictionary if it's a JSON string
            if isinstance(data, str):
                try:
                    data = json.loads(data)
                except json.JSONDecodeError:
                    # If it's not JSON, return as is (might be CSV row)
                    return data

            # Process based on data type
            if data_type == "drivers":
                return self._format_driver_document(data)
            elif data_type == "incidents":
                return self._format_incident_document(data)
            elif data_type == "shipments":
                return self._format_shipment_document(data)
            elif data_type == "vehicles":
                return self._format_vehicle_document(data)
            elif data_type == "invoices":
                return self._format_invoice_document(data)
            else:
                # Default formatting as JSON string
                return json.dumps(data)
        except Exception as e:
            logger.error(f"Error processing document: {e}")
            return ""

    def _format_driver_document(self, data):
        """Format driver data into a document.

        Args:
            data: Driver data

        Returns:
            Formatted document text
        """
        try:
            if isinstance(data, dict):
                driver_id = data.get("id", "Unknown")
                name = data.get("name", "Unknown")
                license_number = data.get("license_number", "Unknown")
                risk_score = data.get("risk_score", "Unknown")
                status = data.get("status", "Unknown")
                vehicle_id = data.get("vehicle_id", "None")
                
                return f"Driver ID: {driver_id}\nName: {name}\nLicense: {license_number}\nRisk Score: {risk_score}\nStatus: {status}\nVehicle ID: {vehicle_id}"
            elif isinstance(data, pd.Series):
                # Handle pandas Series (from CSV)
                return f"Driver ID: {data.get('id', 'Unknown')}\nName: {data.get('name', 'Unknown')}\nLicense: {data.get('license_number', 'Unknown')}\nRisk Score: {data.get('risk_score', 'Unknown')}"
            else:
                return str(data)
        except Exception as e:
            logger.error(f"Error formatting driver document: {e}")
            return str(data)

    def _format_incident_document(self, data):
        """Format incident data into a document.

        Args:
            data: Incident data

        Returns:
            Formatted document text
        """
        try:
            if isinstance(data, dict):
                incident_id = data.get("id", "Unknown")
                driver_id = data.get("driver_id", "Unknown")
                date = data.get("date", "Unknown")
                severity = data.get("severity", "Unknown")
                description = data.get("description", "Unknown")
                location = data.get("location", "Unknown")
                status = data.get("status", "Unknown")
                
                return f"Incident ID: {incident_id}\nDriver ID: {driver_id}\nDate: {date}\nSeverity: {severity}\nDescription: {description}\nLocation: {location}\nStatus: {status}"
            elif isinstance(data, pd.Series):
                # Handle pandas Series (from CSV)
                return f"Incident ID: {data.get('id', 'Unknown')}\nDriver ID: {data.get('driver_id', 'Unknown')}\nDate: {data.get('date', 'Unknown')}\nSeverity: {data.get('severity', 'Unknown')}\nDescription: {data.get('description', 'Unknown')}\nLocation: {data.get('location', 'Unknown')}"
            else:
                return str(data)
        except Exception as e:
            logger.error(f"Error formatting incident document: {e}")
            return str(data)

    def _format_shipment_document(self, data):
        """Format shipment data into a document.

        Args:
            data: Shipment data

        Returns:
            Formatted document text
        """
        try:
            if isinstance(data, dict):
                shipment_id = data.get("id", "Unknown")
                status = data.get("status", "Unknown")
                origin = data.get("origin", {})
                destination = data.get("destination", {})
                cargo = data.get("cargo", {})
                anomalies = data.get("anomalies", [])
                
                origin_str = f"{origin.get('city', 'Unknown')}, {origin.get('country', 'Unknown')}" if isinstance(origin, dict) else str(origin)
                dest_str = f"{destination.get('city', 'Unknown')}, {destination.get('country', 'Unknown')}" if isinstance(destination, dict) else str(destination)
                cargo_str = f"Type: {cargo.get('type', 'Unknown')}, Value: {cargo.get('value', 'Unknown')}" if isinstance(cargo, dict) else str(cargo)
                
                anomaly_str = ""
                if anomalies and isinstance(anomalies, list):
                    for i, anomaly in enumerate(anomalies[:3]):  # Limit to first 3 anomalies
                        if isinstance(anomaly, dict):
                            anomaly_str += f"\nAnomaly {i+1}: {anomaly.get('type', 'Unknown')} - {anomaly.get('description', 'Unknown')} (Severity: {anomaly.get('severity', 'Unknown')})"
                
                return f"Shipment ID: {shipment_id}\nStatus: {status}\nOrigin: {origin_str}\nDestination: {dest_str}\nCargo: {cargo_str}{anomaly_str}"
            else:
                return str(data)
        except Exception as e:
            logger.error(f"Error formatting shipment document: {e}")
            return str(data)

    def _format_vehicle_document(self, data):
        """Format vehicle data into a document.

        Args:
            data: Vehicle data

        Returns:
            Formatted document text
        """
        try:
            if isinstance(data, dict):
                vehicle_id = data.get("id", "Unknown")
                type_val = data.get("type", "Unknown")
                make = data.get("make", "Unknown")
                model = data.get("model", "Unknown")
                year = data.get("year", "Unknown")
                status = data.get("status", "Unknown")
                current_driver_id = data.get("current_driver_id", "None")
                
                return f"Vehicle ID: {vehicle_id}\nType: {type_val}\nMake/Model: {make} {model} ({year})\nStatus: {status}\nCurrent Driver ID: {current_driver_id}"
            else:
                return str(data)
        except Exception as e:
            logger.error(f"Error formatting vehicle document: {e}")
            return str(data)

    def _format_invoice_document(self, data):
        """Format invoice data into a document.

        Args:
            data: Invoice data

        Returns:
            Formatted document text
        """
        try:
            if isinstance(data, dict):
                invoice_id = data.get("id", "Unknown")
                amount = data.get("amount", "Unknown")
                issue_date = data.get("issue_date", "Unknown")
                due_date = data.get("due_date", "Unknown")
                status = data.get("status", "Unknown")
                compliance_flags = data.get("compliance_flags", {})
                
                flags_str = ""
                if compliance_flags and isinstance(compliance_flags, dict):
                    for flag, value in compliance_flags.items():
                        if value:  # Only include true flags
                            flags_str += f"\n- {flag.replace('_', ' ').title()}"
                
                compliance_str = f"\nCompliance Issues:{flags_str}" if flags_str else "\nNo compliance issues."
                
                return f"Invoice ID: {invoice_id}\nAmount: ${amount}\nIssue Date: {issue_date}\nDue Date: {due_date}\nStatus: {status}{compliance_str}"
            else:
                return str(data)
        except Exception as e:
            logger.error(f"Error formatting invoice document: {e}")
            return str(data)

    def _format_context(self, data_types, documents, scores):
        """Format retrieved documents into context for the LLM.

        Args:
            data_types: List of data types
            documents: List of retrieved documents
            scores: List of relevance scores

        Returns:
            Formatted context string
        """
        # Sort by score (highest first)
        sorted_results = sorted(zip(data_types, documents, scores), key=lambda x: x[2], reverse=True)
        
        context = "\n\nRelevant information:\n"
        for i, (data_type, doc, score) in enumerate(sorted_results[:10]):  # Limit to top 10
            context += f"\n--- {data_type.upper()} DOCUMENT {i+1} (Relevance: {score:.2f}) ---\n{doc}\n"
        
        return context

    def _generate_prompt(self, query, context):
        """Generate a prompt for the LLM.

        Args:
            query: User query
            context: Retrieved context

        Returns:
            Formatted prompt
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        prompt = f"""You are LogisticsPulse, an AI assistant for a logistics company. 
        The current time is {current_time}.
        
        Answer the following query based ONLY on the provided context. If the context doesn't contain relevant information to answer the query, say that you don't have enough information and suggest what data might help answer the query.
        
        Be concise, professional, and focus on actionable insights. If there are anomalies, incidents, or compliance issues mentioned in the context, highlight them clearly.
        
        {context}
        
        Query: {query}
        
        Answer:"""
        
        return prompt

    def _generate_fallback_prompt(self, query):
        """Generate a fallback prompt when no context is available.

        Args:
            query: User query

        Returns:
            Formatted prompt
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        prompt = f"""You are LogisticsPulse, an AI assistant for a logistics company. 
        The current time is {current_time}.
        
        I don't have specific data to answer the following query. Please provide a general response based on your knowledge of logistics operations, but make it clear that you don't have access to the specific data requested.
        
        Query: {query}
        
        Answer:"""
        
        return prompt

    def run(self):
        """Run the pipeline."""
        logger.info("Starting LogisticsPulse RAG pipeline")
        logger.info(f"Monitoring data directories: {list(self.data_dirs.keys())}")
        
        # Build and run the pipeline
        self.build_pipeline()
        
        try:
            # Keep the pipeline running
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            logger.info("Pipeline stopped by user")
        except Exception as e:
            logger.error(f"Pipeline error: {e}")
        finally:
            if self.pw_context:
                self.pw_context.stop()


def run_rag_pipeline(config):
    """Run the RAG pipeline.

    Args:
        config: Configuration dictionary

    Returns:
        None
    """
    pipeline = LogisticsRAGPipeline(config)
    pipeline.run()


if __name__ == "__main__":
    import argparse
    import yaml

    parser = argparse.ArgumentParser(description='Run LogisticsPulse RAG pipeline')
    parser.add_argument('--config', required=True, help='Path to configuration YAML file')

    args = parser.parse_args()

    # Load configuration
    with open(args.config, 'r') as f:
        config = yaml.safe_load(f)

    run_rag_pipeline(config)