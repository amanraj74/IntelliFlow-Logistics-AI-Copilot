import React, { useState, useEffect } from 'react';
import { Card, Table, Badge, Tabs, Space, Button, Tooltip, Modal, Typography, Timeline, Statistic, Row, Col, Alert } from 'antd';
import { MapContainer, TileLayer, Marker, Popup, Polyline } from 'react-leaflet';
import { WarningOutlined, CheckCircleOutlined, ClockCircleOutlined, ExclamationCircleOutlined, CarOutlined, LineChartOutlined } from '@ant-design/icons';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';

// Fix for Leaflet marker icons in React
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.7.1/dist/images/marker-shadow.png',
});

const { TabPane } = Tabs;
const { Title, Text } = Typography;

const ShipmentAnomalyDashboard = () => {
  const [shipments, setShipments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [selectedShipment, setSelectedShipment] = useState(null);
  const [modalVisible, setModalVisible] = useState(false);
  const [anomalyStats, setAnomalyStats] = useState({
    total: 0,
    high: 0,
    medium: 0,
    low: 0,
    byType: {}
  });

  // Fetch shipment data
  useEffect(() => {
    const fetchData = async () => {
      try {
        // In a real application, this would be an API call
        // For demo purposes, we'll simulate a delay and use mock data
        setTimeout(() => {
          const mockShipments = generateMockShipments();
          setShipments(mockShipments);
          calculateAnomalyStats(mockShipments);
          setLoading(false);
        }, 1000);
      } catch (error) {
        console.error('Error fetching shipment data:', error);
        setLoading(false);
      }
    };

    fetchData();

    // Set up polling for real-time updates
    const intervalId = setInterval(() => {
      fetchData();
    }, 30000); // Poll every 30 seconds

    return () => clearInterval(intervalId);
  }, []);

  const calculateAnomalyStats = (shipmentData) => {
    const stats = {
      total: 0,
      high: 0,
      medium: 0,
      low: 0,
      byType: {}
    };

    shipmentData.forEach(shipment => {
      if (shipment.anomalies && shipment.anomalies.length > 0) {
        stats.total += shipment.anomalies.length;
        
        shipment.anomalies.forEach(anomaly => {
          // Count by severity
          if (anomaly.severity === 'high') stats.high++;
          else if (anomaly.severity === 'medium') stats.medium++;
          else if (anomaly.severity === 'low') stats.low++;
          
          // Count by type
          if (!stats.byType[anomaly.type]) {
            stats.byType[anomaly.type] = 0;
          }
          stats.byType[anomaly.type]++;
        });
      }
    });

    setAnomalyStats(stats);
  };

  const showShipmentDetails = (shipment) => {
    setSelectedShipment(shipment);
    setModalVisible(true);
  };

  const getSeverityBadge = (severity) => {
    switch (severity) {
      case 'high':
        return <Badge status="error" text="High" />;
      case 'medium':
        return <Badge status="warning" text="Medium" />;
      case 'low':
        return <Badge status="processing" text="Low" />;
      default:
        return <Badge status="default" text="Unknown" />;
    }
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'in_transit':
        return <Badge status="processing" text="In Transit" />;
      case 'delivered':
        return <Badge status="success" text="Delivered" />;
      case 'delayed':
        return <Badge status="warning" text="Delayed" />;
      case 'cancelled':
        return <Badge status="error" text="Cancelled" />;
      default:
        return <Badge status="default" text={status} />;
    }
  };

  const columns = [
    {
      title: 'Shipment ID',
      dataIndex: 'id',
      key: 'id',
      render: (text) => <a>{text}</a>,
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      render: (status) => getStatusBadge(status),
    },
    {
      title: 'Origin',
      dataIndex: ['origin', 'city'],
      key: 'origin',
    },
    {
      title: 'Destination',
      dataIndex: ['destination', 'city'],
      key: 'destination',
    },
    {
      title: 'Anomalies',
      key: 'anomalies',
      render: (_, record) => (
        <Space>
          {record.anomalies && record.anomalies.length > 0 ? (
            <Badge count={record.anomalies.length} style={{ backgroundColor: record.has_high_severity_anomalies ? '#f5222d' : '#faad14' }} />
          ) : (
            <Badge count={0} showZero style={{ backgroundColor: '#52c41a' }} />
          )}
        </Space>
      ),
    },
    {
      title: 'Actions',
      key: 'actions',
      render: (_, record) => (
        <Space size="middle">
          <Button type="primary" size="small" onClick={() => showShipmentDetails(record)}>
            View Details
          </Button>
        </Space>
      ),
    },
  ];

  return (
    <div style={{ padding: '20px' }}>
      <Title level={2}>Shipment Anomaly Dashboard</Title>
      
      <Row gutter={16} style={{ marginBottom: '20px' }}>
        <Col span={6}>
          <Card>
            <Statistic 
              title="Total Anomalies" 
              value={anomalyStats.total} 
              valueStyle={{ color: anomalyStats.total > 0 ? '#cf1322' : '#3f8600' }}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="High Severity" 
              value={anomalyStats.high} 
              valueStyle={{ color: '#cf1322' }}
              prefix={<WarningOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="Medium Severity" 
              value={anomalyStats.medium} 
              valueStyle={{ color: '#faad14' }}
              prefix={<ExclamationCircleOutlined />}
            />
          </Card>
        </Col>
        <Col span={6}>
          <Card>
            <Statistic 
              title="Low Severity" 
              value={anomalyStats.low} 
              valueStyle={{ color: '#1890ff' }}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      {anomalyStats.total > 0 && (
        <Alert
          message="Active Anomalies Detected"
          description="There are active anomalies that require attention. Review the shipments below for details."
          type="warning"
          showIcon
          style={{ marginBottom: '20px' }}
        />
      )}
      
      <Card title="Shipments" extra={<Button type="primary">Refresh Data</Button>}>
        <Table 
          columns={columns} 
          dataSource={shipments} 
          rowKey="id" 
          loading={loading}
          pagination={{ pageSize: 10 }}
        />
      </Card>

      {selectedShipment && (
        <Modal
          title={`Shipment ${selectedShipment.id} Details`}
          visible={modalVisible}
          onCancel={() => setModalVisible(false)}
          width={1000}
          footer={[
            <Button key="close" onClick={() => setModalVisible(false)}>
              Close
            </Button>,
          ]}
        >
          <Tabs defaultActiveKey="1">
            <TabPane tab="Overview" key="1">
              <Row gutter={16}>
                <Col span={12}>
                  <Card title="Shipment Information" bordered={false}>
                    <p><strong>Status:</strong> {getStatusBadge(selectedShipment.status)}</p>
                    <p><strong>Origin:</strong> {selectedShipment.origin.city}, {selectedShipment.origin.country}</p>
                    <p><strong>Destination:</strong> {selectedShipment.destination.city}, {selectedShipment.destination.country}</p>
                    <p><strong>Estimated Arrival:</strong> {selectedShipment.estimated_arrival_time}</p>
                    {selectedShipment.actual_arrival_time && (
                      <p><strong>Actual Arrival:</strong> {selectedShipment.actual_arrival_time}</p>
                    )}
                  </Card>
                </Col>
                <Col span={12}>
                  <Card title="Cargo Information" bordered={false}>
                    <p><strong>Type:</strong> {selectedShipment.cargo.type}</p>
                    <p><strong>Value:</strong> ${selectedShipment.cargo.value.toLocaleString()}</p>
                    <p><strong>Weight:</strong> {selectedShipment.cargo.weight} kg</p>
                    {selectedShipment.cargo.temperature_controlled && (
                      <p><strong>Temperature Range:</strong> {selectedShipment.cargo.temperature_range.min}°C to {selectedShipment.cargo.temperature_range.max}°C</p>
                    )}
                  </Card>
                </Col>
              </Row>

              {selectedShipment.anomalies && selectedShipment.anomalies.length > 0 && (
                <Card title="Detected Anomalies" style={{ marginTop: '20px' }} className="anomaly-card">
                  <Timeline>
                    {selectedShipment.anomalies.map((anomaly, index) => (
                      <Timeline.Item 
                        key={index} 
                        color={anomaly.severity === 'high' ? 'red' : anomaly.severity === 'medium' ? 'orange' : 'blue'}
                      >
                        <p><strong>{anomaly.type.replace('_', ' ').toUpperCase()}</strong> - {getSeverityBadge(anomaly.severity)}</p>
                        <p>{anomaly.description}</p>
                        <p><small>Detected at: {anomaly.timestamp}</small></p>
                        {anomaly.location && (
                          <p><small>Location: {anomaly.location.latitude.toFixed(4)}, {anomaly.location.longitude.toFixed(4)}</small></p>
                        )}
                      </Timeline.Item>
                    ))}
                  </Timeline>
                </Card>
              )}
            </TabPane>
            
            <TabPane tab="Route Map" key="2">
              {selectedShipment.actual_route && selectedShipment.actual_route.length > 0 ? (
                <div style={{ height: '500px', width: '100%' }}>
                  <MapContainer 
                    center={[selectedShipment.actual_route[0].latitude, selectedShipment.actual_route[0].longitude]} 
                    zoom={8} 
                    style={{ height: '100%', width: '100%' }}
                  >
                    <TileLayer
                      url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
                      attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
                    />
                    
                    {/* Origin marker */}
                    <Marker position={[selectedShipment.origin.coordinates.latitude, selectedShipment.origin.coordinates.longitude]}>
                      <Popup>Origin: {selectedShipment.origin.city}</Popup>
                    </Marker>
                    
                    {/* Destination marker */}
                    <Marker position={[selectedShipment.destination.coordinates.latitude, selectedShipment.destination.coordinates.longitude]}>
                      <Popup>Destination: {selectedShipment.destination.city}</Popup>
                    </Marker>
                    
                    {/* Actual route line */}
                    <Polyline 
                      positions={selectedShipment.actual_route.map(point => [point.latitude, point.longitude])}
                      color="blue"
                    />
                    
                    {/* Planned route line (if available) */}
                    {selectedShipment.planned_route && (
                      <Polyline 
                        positions={selectedShipment.planned_route.map(point => [point.latitude, point.longitude])}
                        color="green"
                        dashArray="5, 5"
                      />
                    )}
                    
                    {/* Anomaly markers */}
                    {selectedShipment.anomalies && selectedShipment.anomalies.map((anomaly, index) => {
                      if (anomaly.location) {
                        return (
                          <Marker 
                            key={index} 
                            position={[anomaly.location.latitude, anomaly.location.longitude]}
                            icon={new L.Icon({
                              iconUrl: 'https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-red.png',
                              shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/0.7.7/images/marker-shadow.png',
                              iconSize: [25, 41],
                              iconAnchor: [12, 41],
                              popupAnchor: [1, -34],
                              shadowSize: [41, 41]
                            })}
                          >
                            <Popup>
                              <strong>{anomaly.type.replace('_', ' ')}</strong><br />
                              {anomaly.description}<br />
                              <small>Severity: {anomaly.severity}</small>
                            </Popup>
                          </Marker>
                        );
                      }
                      return null;
                    })}
                  </MapContainer>
                </div>
              ) : (
                <Alert message="No route data available for this shipment" type="info" />
              )}
            </TabPane>
          </Tabs>
        </Modal>
      )}
    </div>
  );
};

// Mock data generator for demo purposes
const generateMockShipments = () => {
  return [
    {
      id: 'SHP-1001',
      status: 'in_transit',
      origin: {
        city: 'Los Angeles',
        country: 'USA',
        coordinates: {
          latitude: 34.0522,
          longitude: -118.2437
        }
      },
      destination: {
        city: 'New York',
        country: 'USA',
        coordinates: {
          latitude: 40.7128,
          longitude: -74.0060
        }
      },
      estimated_arrival_time: '2023-05-15T14:00:00Z',
      cargo: {
        type: 'Electronics',
        value: 250000,
        weight: 2500,
        temperature_controlled: false
      },
      actual_route: [
        { latitude: 34.0522, longitude: -118.2437, timestamp: '2023-05-10T08:00:00Z', speed: 0 },
        { latitude: 35.1983, longitude: -111.6513, timestamp: '2023-05-10T14:00:00Z', speed: 75 },
        { latitude: 35.9728, longitude: -101.8968, timestamp: '2023-05-11T02:00:00Z', speed: 80 },
        { latitude: 37.6872, longitude: -97.3301, timestamp: '2023-05-11T10:00:00Z', speed: 70 },
        { latitude: 38.2527, longitude: -85.7585, timestamp: '2023-05-12T04:00:00Z', speed: 65 },
        { latitude: 39.1031, longitude: -84.5120, timestamp: '2023-05-12T08:00:00Z', speed: 0 },
        { latitude: 39.1031, longitude: -84.5120, timestamp: '2023-05-12T10:00:00Z', speed: 0 },
        { latitude: 39.9612, longitude: -82.9988, timestamp: '2023-05-12T14:00:00Z', speed: 75 },
      ],
      planned_route: [
        { latitude: 34.0522, longitude: -118.2437, timestamp: '2023-05-10T08:00:00Z' },
        { latitude: 36.1699, longitude: -115.1398, timestamp: '2023-05-10T14:00:00Z' },
        { latitude: 39.7392, longitude: -104.9903, timestamp: '2023-05-11T02:00:00Z' },
        { latitude: 41.2565, longitude: -95.9345, timestamp: '2023-05-11T14:00:00Z' },
        { latitude: 41.8781, longitude: -87.6298, timestamp: '2023-05-12T02:00:00Z' },
        { latitude: 40.7128, longitude: -74.0060, timestamp: '2023-05-12T14:00:00Z' },
      ],
      anomalies: [
        {
          type: 'route_deviation',
          description: 'Route deviation of 180.5 km detected',
          severity: 'medium',
          timestamp: '2023-05-11T02:00:00Z',
          location: {
            latitude: 35.9728,
            longitude: -101.8968
          },
          resolved: false
        },
        {
          type: 'unusual_stop',
          description: 'Unusual stop detected for 120.0 minutes',
          severity: 'high',
          timestamp: '2023-05-12T08:00:00Z',
          location: {
            latitude: 39.1031,
            longitude: -84.5120
          },
          resolved: false
        }
      ],
      has_high_severity_anomalies: true
    },
    {
      id: 'SHP-1002',
      status: 'delivered',
      origin: {
        city: 'Chicago',
        country: 'USA',
        coordinates: {
          latitude: 41.8781,
          longitude: -87.6298
        }
      },
      destination: {
        city: 'Detroit',
        country: 'USA',
        coordinates: {
          latitude: 42.3314,
          longitude: -83.0458
        }
      },
      estimated_arrival_time: '2023-05-11T10:00:00Z',
      actual_arrival_time: '2023-05-11T09:45:00Z',
      cargo: {
        type: 'Automotive Parts',
        value: 120000,
        weight: 3200,
        temperature_controlled: false
      },
      actual_route: [
        { latitude: 41.8781, longitude: -87.6298, timestamp: '2023-05-10T08:00:00Z', speed: 0 },
        { latitude: 41.9742, longitude: -86.1765, timestamp: '2023-05-10T12:00:00Z', speed: 70 },
        { latitude: 42.3223, longitude: -85.1792, timestamp: '2023-05-10T16:00:00Z', speed: 75 },
        { latitude: 42.3314, longitude: -83.0458, timestamp: '2023-05-11T09:45:00Z', speed: 0 },
      ],
      anomalies: [],
      has_high_severity_anomalies: false
    },
    {
      id: 'SHP-1003',
      status: 'in_transit',
      origin: {
        city: 'Miami',
        country: 'USA',
        coordinates: {
          latitude: 25.7617,
          longitude: -80.1918
        }
      },
      destination: {
        city: 'Atlanta',
        country: 'USA',
        coordinates: {
          latitude: 33.7490,
          longitude: -84.3880
        }
      },
      estimated_arrival_time: '2023-05-14T18:00:00Z',
      cargo: {
        type: 'Perishable Goods',
        value: 85000,
        weight: 1800,
        temperature_controlled: true,
        temperature_range: {
          min: 2,
          max: 8
        }
      },
      actual_route: [
        { latitude: 25.7617, longitude: -80.1918, timestamp: '2023-05-12T08:00:00Z', speed: 0, temperature: 5 },
        { latitude: 26.1224, longitude: -80.1373, timestamp: '2023-05-12T09:00:00Z', speed: 65, temperature: 4 },
        { latitude: 27.3364, longitude: -81.3369, timestamp: '2023-05-12T12:00:00Z', speed: 70, temperature: 10 },
        { latitude: 28.5383, longitude: -81.3792, timestamp: '2023-05-12T15:00:00Z', speed: 75, temperature: 12 },
        { latitude: 30.3322, longitude: -81.6557, timestamp: '2023-05-12T18:00:00Z', speed: 80, temperature: 9 },
      ],
      anomalies: [
        {
          type: 'temperature_breach',
          description: 'Temperature too high: 12°C (max: 8°C)',
          severity: 'high',
          timestamp: '2023-05-12T15:00:00Z',
          location: {
            latitude: 28.5383,
            longitude: -81.3792
          },
          resolved: false
        }
      ],
      has_high_severity_anomalies: true
    },
    {
      id: 'SHP-1004',
      status: 'delayed',
      origin: {
        city: 'Seattle',
        country: 'USA',
        coordinates: {
          latitude: 47.6062,
          longitude: -122.3321
        }
      },
      destination: {
        city: 'Portland',
        country: 'USA',
        coordinates: {
          latitude: 45.5051,
          longitude: -122.6750
        }
      },
      estimated_arrival_time: '2023-05-12T16:00:00Z',
      cargo: {
        type: 'Furniture',
        value: 45000,
        weight: 2200,
        temperature_controlled: false
      },
      actual_route: [
        { latitude: 47.6062, longitude: -122.3321, timestamp: '2023-05-12T08:00:00Z', speed: 0 },
        { latitude: 47.2529, longitude: -122.4443, timestamp: '2023-05-12T09:00:00Z', speed: 60 },
        { latitude: 46.8761, longitude: -122.7346, timestamp: '2023-05-12T10:00:00Z', speed: 0 },
        { latitude: 46.8761, longitude: -122.7346, timestamp: '2023-05-12T14:00:00Z', speed: 0 },
      ],
      anomalies: [
        {
          type: 'delay',
          description: 'Projected delay of 4.5 hours based on current progress',
          severity: 'medium',
          timestamp: '2023-05-12T14:00:00Z',
          location: {
            latitude: 46.8761,
            longitude: -122.7346
          },
          resolved: false
        },
        {
          type: 'unusual_stop',
          description: 'Unusual stop detected for 240.0 minutes',
          severity: 'high',
          timestamp: '2023-05-12T10:00:00Z',
          location: {
            latitude: 46.8761,
            longitude: -122.7346
          },
          resolved: false
        }
      ],
      has_high_severity_anomalies: true
    },
    {
      id: 'SHP-1005',
      status: 'in_transit',
      origin: {
        city: 'Boston',
        country: 'USA',
        coordinates: {
          latitude: 42.3601,
          longitude: -71.0589
        }
      },
      destination: {
        city: 'Philadelphia',
        country: 'USA',
        coordinates: {
          latitude: 39.9526,
          longitude: -75.1652
        }
      },
      estimated_arrival_time: '2023-05-13T12:00:00Z',
      cargo: {
        type: 'Pharmaceuticals',
        value: 320000,
        weight: 800,
        temperature_controlled: true,
        temperature_range: {
          min: 15,
          max: 25
        }
      },
      actual_route: [
        { latitude: 42.3601, longitude: -71.0589, timestamp: '2023-05-12T08:00:00Z', speed: 0, temperature: 20 },
        { latitude: 41.8240, longitude: -71.4128, timestamp: '2023-05-12T09:30:00Z', speed: 75, temperature: 18 },
        { latitude: 41.3583, longitude: -72.0950, timestamp: '2023-05-12T11:00:00Z', speed: 80, temperature: 19 },
        { latitude: 40.8224, longitude: -73.0120, timestamp: '2023-05-12T12:30:00Z', speed: 130, temperature: 21 },
        { latitude: 40.7128, longitude: -74.0060, timestamp: '2023-05-12T13:30:00Z', speed: 70, temperature: 20 },
      ],
      anomalies: [
        {
          type: 'speed_violation',
          description: 'Speed violation detected: 130.0 km/h',
          severity: 'high',
          timestamp: '2023-05-12T12:30:00Z',
          location: {
            latitude: 40.8224,
            longitude: -73.0120
          },
          resolved: false
        }
      ],
      has_high_severity_anomalies: true
    }
  ];
};

export default ShipmentAnomalyDashboard;