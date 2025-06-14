import React, { useState, useEffect, useRef } from 'react';
import './App.css';
import mqtt from 'mqtt';
import { Line } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';

// Register Chart.js components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  Title,
  Tooltip,
  Legend
);

// MQTT broker configuration - using multiple public brokers for redundancy
const MQTT_BROKERS = [
  {url: 'ws://broker.hivemq.com:8000/mqtt', name: 'HiveMQ (WS)'},
  {url: 'wss://broker.hivemq.com:8884/mqtt', name: 'HiveMQ (WSS)'},
  {url: 'ws://broker.emqx.io:8083/mqtt', name: 'EMQX (WS)'},
  {url: 'wss://broker.emqx.io:8084/mqtt', name: 'EMQX (WSS)'},
];
const TOPIC_BASE = 'cansat/estacao/teste1';

function App() {  const [connected, setConnected] = useState(false);  const [messageReceived, setMessageReceived] = useState(false);
  const [debugMessages, setDebugMessages] = useState([]);
  const [showDebug, setShowDebug] = useState(false);
  const [activeBroker, setActiveBroker] = useState(0);
  const [metrics, setMetrics] = useState({
    temperature: [],
    pressure: [],
    accelerationX: [],
    accelerationY: [],
    accelerationZ: [],
    gyroX: [],
    gyroY: [],
    gyroZ: [],
  });

  const [currentMetrics, setCurrentMetrics] = useState({
    temperature: 0,
    pressure: 0,
    accelerationX: 0,
    accelerationY: 0,
    accelerationZ: 0,
    gyroX: 0,
    gyroY: 0,
    gyroZ: 0,
    lastUpdate: null,
  });

  const clientRef = useRef(null);
  const maxDataPoints = 30;
  useEffect(() => {
    // Create MQTT client using the active broker
    const broker = MQTT_BROKERS[activeBroker];
    console.log(`Tentando conectar a ${broker.name}: ${broker.url}`);
    
    const client = mqtt.connect(broker.url);
    clientRef.current = client;    // Setup event handlers
    client.on('connect', () => {
      console.log(`Conectado ao broker MQTT: ${MQTT_BROKERS[activeBroker].name}`);
      setConnected(true);
      
      // Subscribe to all data topics
      client.subscribe(`${TOPIC_BASE}/raw`);
      client.subscribe(`${TOPIC_BASE}/temperatura`);
      client.subscribe(`${TOPIC_BASE}/pressao`);
      client.subscribe(`${TOPIC_BASE}/accelX`);
      client.subscribe(`${TOPIC_BASE}/accelY`);
      client.subscribe(`${TOPIC_BASE}/accelZ`);
      client.subscribe(`${TOPIC_BASE}/gyroX`);
      client.subscribe(`${TOPIC_BASE}/gyroY`);
      client.subscribe(`${TOPIC_BASE}/gyroZ`);
    });    client.on('message', (topic, message) => {
      const value = message.toString();
      const now = new Date();
      // Debug: mostrar todas as mensagens recebidas no console
      console.log(`Mensagem recebida no tópico ${topic}:`, value);
      
      // Adicionar à lista de mensagens de depuração
      setDebugMessages(prev => {
        const newMessages = [...prev, {
          time: now.toLocaleTimeString(),
          topic,
          value
        }];
        return newMessages.slice(-20); // Manter apenas as últimas 20 mensagens
      });
      
      // Atualizar indicador de recebimento de mensagens
      setMessageReceived(true);
      setTimeout(() => setMessageReceived(false), 1000);      // Process raw messages
      if (topic === `${TOPIC_BASE}/raw`) {
        // Parse using regex to extract values - agora com suporte para "ovf" (overflow)
        const dataRegex = /ID: (\d+) \| Temperatura: ([\d\.-]+) C \| Pressao: ([\d\.-]+) hPa \| Accel \[X,Y,Z\]: ([\d\.-]+), ([\d\.-]+), ([\d\.-]+) \| Gyro \[X,Y,Z\] \(°\/s\): ([\d\.-]+|ovf), ([\d\.-]+|ovf), ([\d\.-]+|ovf)/;
        const match = value.match(dataRegex);
        
        if (match) {          const [_, id, temp, press, accelX, accelY, accelZ, gyroX, gyroY, gyroZ] = match;
          
          // Função para converter valores para float, lidando com "ovf" (overflow)
          const parseValue = (val) => {
            return val === 'ovf' ? null : parseFloat(val);
          };
          
          // Update current metrics
          setCurrentMetrics({
            temperature: parseFloat(temp),
            pressure: parseFloat(press),
            accelerationX: parseFloat(accelX),
            accelerationY: parseFloat(accelY),
            accelerationZ: parseFloat(accelZ),
            gyroX: parseValue(gyroX),
            gyroY: parseValue(gyroY),
            gyroZ: parseValue(gyroZ),
            lastUpdate: now,
          });
          
          // Update time series data
          setMetrics(prev => {
            const timestamp = now.toLocaleTimeString();
            
            // Helper function to add new data point and maintain max length
            const updateMetric = (arr, value) => {
              const newArr = [...arr, { x: timestamp, y: parseFloat(value) }];
              return newArr.length > maxDataPoints ? newArr.slice(-maxDataPoints) : newArr;
            };
            
            return {              temperature: updateMetric(prev.temperature, temp),
              pressure: updateMetric(prev.pressure, press),
              accelerationX: updateMetric(prev.accelerationX, accelX),
              accelerationY: updateMetric(prev.accelerationY, accelY),
              accelerationZ: updateMetric(prev.accelerationZ, accelZ),
              gyroX: gyroX !== 'ovf' ? updateMetric(prev.gyroX, gyroX) : prev.gyroX,
              gyroY: gyroY !== 'ovf' ? updateMetric(prev.gyroY, gyroY) : prev.gyroY,
              gyroZ: gyroZ !== 'ovf' ? updateMetric(prev.gyroZ, gyroZ) : prev.gyroZ,
            };
          });
        }
      } 
      // Process individual topic data
      else {
        const metricMap = {
          [`${TOPIC_BASE}/temperatura`]: 'temperature',
          [`${TOPIC_BASE}/pressao`]: 'pressure',
          [`${TOPIC_BASE}/accelX`]: 'accelerationX',
          [`${TOPIC_BASE}/accelY`]: 'accelerationY',
          [`${TOPIC_BASE}/accelZ`]: 'accelerationZ',
          [`${TOPIC_BASE}/gyroX`]: 'gyroX',
          [`${TOPIC_BASE}/gyroY`]: 'gyroY',
          [`${TOPIC_BASE}/gyroZ`]: 'gyroZ',
        };
        
        const metricKey = metricMap[topic];
        if (metricKey) {
          const numericValue = parseFloat(value);
          
          // Update current value
          setCurrentMetrics(prev => ({
            ...prev,
            [metricKey]: numericValue,
            lastUpdate: now,
          }));
          
          // Update timeseries
          setMetrics(prev => {
            const timestamp = now.toLocaleTimeString();
            const newArr = [...prev[metricKey], { x: timestamp, y: numericValue }];
            return {
              ...prev,
              [metricKey]: newArr.length > maxDataPoints ? newArr.slice(-maxDataPoints) : newArr,
            };
          });
        }
      }
    });    // Setup error handler
    client.on('error', (error) => {
      console.error('MQTT error:', error);
      setConnected(false);
      
      // Try next broker on error
      const nextBroker = (activeBroker + 1) % MQTT_BROKERS.length;
      console.log(`Erro de conexão. Tentando próximo broker: ${MQTT_BROKERS[nextBroker].name}`);
      setActiveBroker(nextBroker);
    });
    
    client.on('close', () => {
      console.log('MQTT connection closed');
      setConnected(false);
    });

    // Cleanup on component unmount
    return () => {
      if (client) {
        client.end();
      }
    };
  }, [activeBroker]); // Reconnect when active broker changes

  // Chart options
  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    animation: {
      duration: 0
    },
    scales: {
      y: {
        beginAtZero: false,
      },
    },
    plugins: {
      legend: {
        position: 'top',
      },
    },
  };
  // Chart data function
  const getChartData = (data, label, color) => {
    // Se não houver dados ainda, mostrar um placeholder
    if (data.length === 0) {
      return {
        labels: ['Aguardando dados...'],
        datasets: [
          {
            label,
            data: [0],
            borderColor: color,
            backgroundColor: `${color}33`,
            fill: true,
            tension: 0.4,
          },
        ],
      };
    }
    
    return {
      labels: data.map(point => point.x),
      datasets: [
        {
          label,
          data: data.map(point => point.y),
          borderColor: color,
          backgroundColor: `${color}33`,
          fill: true,
          tension: 0.4,
        },
      ],
    };
  };

  return (
    <div className="App">      <header className="App-header">
        <h1>CanSat Dashboard</h1>        <div className="connection-status">
          Status: {connected ? 
            <span className="connected">Connected ({MQTT_BROKERS[activeBroker].name})</span> : 
            <span className="disconnected">Disconnected</span>          }
          {messageReceived && <span className="message-indicator">●</span>}
          <button className="debug-toggle" onClick={() => setShowDebug(!showDebug)}>
            {showDebug ? 'Ocultar Debug' : 'Mostrar Debug'}
          </button>
          <select 
            className="broker-selector"
            value={activeBroker}
            onChange={(e) => setActiveBroker(parseInt(e.target.value))}
          >
            {MQTT_BROKERS.map((broker, idx) => (
              <option key={idx} value={idx}>
                {broker.name}
              </option>
            ))}
          </select>
          <button 
            className="reconnect-button" 
            onClick={() => setActiveBroker((prev) => prev)}
            title="Force reconnection to the broker"
          >
            Reconectar
          </button>
        </div>
      </header>

      <div className="dashboard-container">
        <div className="metrics-panel">
          <h2>Current Readings</h2>
          <div className="metrics-grid">
            <div className="metric-card">
              <h3>Temperature</h3>
              <div className="metric-value">{currentMetrics.temperature.toFixed(2)} °C</div>
            </div>
            <div className="metric-card">
              <h3>Pressure</h3>
              <div className="metric-value">{currentMetrics.pressure.toFixed(2)} hPa</div>
            </div>
            <div className="metric-card">
              <h3>Acceleration X</h3>
              <div className="metric-value">{currentMetrics.accelerationX.toFixed(3)}</div>
            </div>
            <div className="metric-card">
              <h3>Acceleration Y</h3>
              <div className="metric-value">{currentMetrics.accelerationY.toFixed(3)}</div>
            </div>
            <div className="metric-card">
              <h3>Acceleration Z</h3>
              <div className="metric-value">{currentMetrics.accelerationZ.toFixed(3)}</div>
            </div>            <div className="metric-card">
              <h3>Gyro X</h3>
              <div className="metric-value">
                {currentMetrics.gyroX !== null ? `${currentMetrics.gyroX.toFixed(2)} °/s` : 'overflow'}
              </div>
            </div>
            <div className="metric-card">
              <h3>Gyro Y</h3>
              <div className="metric-value">
                {currentMetrics.gyroY !== null ? `${currentMetrics.gyroY.toFixed(2)} °/s` : 'overflow'}
              </div>
            </div>
            <div className="metric-card">
              <h3>Gyro Z</h3>
              <div className="metric-value">
                {currentMetrics.gyroZ !== null ? `${currentMetrics.gyroZ.toFixed(2)} °/s` : 'overflow'}
              </div>
            </div>
          </div>
          {currentMetrics.lastUpdate && (
            <div className="last-update">
              Last update: {currentMetrics.lastUpdate.toLocaleTimeString()}
            </div>
          )}
        </div>

        <div className="charts-container">
          <div className="chart-row">
            <div className="chart-container">
              <h3>Temperature</h3>
              <Line 
                options={chartOptions} 
                data={getChartData(metrics.temperature, 'Temperature (°C)', '#ff6384')} 
              />
            </div>
            <div className="chart-container">
              <h3>Pressure</h3>
              <Line 
                options={chartOptions} 
                data={getChartData(metrics.pressure, 'Pressure (hPa)', '#36a2eb')} 
              />
            </div>
          </div>
          <div className="chart-row">
            <div className="chart-container">
              <h3>Acceleration</h3>
              <Line 
                options={chartOptions} 
                data={{
                  labels: metrics.accelerationX.map(point => point.x),
                  datasets: [
                    {
                      label: 'X',
                      data: metrics.accelerationX.map(point => point.y),
                      borderColor: '#ff6384',
                      backgroundColor: 'transparent',
                    },
                    {
                      label: 'Y',
                      data: metrics.accelerationY.map(point => point.y),
                      borderColor: '#36a2eb',
                      backgroundColor: 'transparent',
                    },
                    {
                      label: 'Z',
                      data: metrics.accelerationZ.map(point => point.y),
                      borderColor: '#4bc0c0',
                      backgroundColor: 'transparent',
                    },
                  ],
                }}
              />
            </div>
            <div className="chart-container">
              <h3>Gyroscope</h3>
              <Line 
                options={chartOptions} 
                data={{
                  labels: metrics.gyroX.map(point => point.x),
                  datasets: [
                    {
                      label: 'X (°/s)',
                      data: metrics.gyroX.map(point => point.y),
                      borderColor: '#ff6384',
                      backgroundColor: 'transparent',
                    },
                    {
                      label: 'Y (°/s)',
                      data: metrics.gyroY.map(point => point.y),
                      borderColor: '#36a2eb',
                      backgroundColor: 'transparent',
                    },
                    {
                      label: 'Z (°/s)',
                      data: metrics.gyroZ.map(point => point.y),
                      borderColor: '#4bc0c0',
                      backgroundColor: 'transparent',
                    },
                  ],
                }}
              />
            </div>
          </div>
        </div>
      </div>      <footer>
        <p>
          CanSat Dashboard &copy; {new Date().getFullYear()} | 
          MQTT Status: {connected ? "Connected" : "Disconnected"} |
          <button 
            onClick={() => {
              if (clientRef.current) {
                const testMessage = {
                  id: 9999,
                  temperature: 25.5,
                  pressure: 1013.25,
                  accelX: 0.1,
                  accelY: 0.2,
                  accelZ: 9.8,
                  gyroX: 1.1,
                  gyroY: 2.2,
                  gyroZ: 0.5,
                  timestamp: new Date().toISOString()
                };
                clientRef.current.publish(`${TOPIC_BASE}/test`, JSON.stringify(testMessage));
                console.log('Mensagem de teste enviada');
                alert('Mensagem de teste enviada. Verifique o console para mais detalhes.');
              }
            }}
            className="test-button"
          >
            Enviar mensagem de teste
          </button>
        </p>      </footer>
      
      {showDebug && (
        <div className="debug-panel">
          <h3>Debug Console</h3>
          <div className="debug-messages">
            {debugMessages.length === 0 ? (
              <p className="no-messages">Nenhuma mensagem recebida</p>
            ) : (
              <ul>
                {debugMessages.map((msg, idx) => (
                  <li key={idx}>
                    <span className="time">{msg.time}</span>
                    <span className="topic">{msg.topic}</span>
                    <span className="value">{msg.value}</span>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default App;
