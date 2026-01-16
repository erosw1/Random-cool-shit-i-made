import React, { useState, useEffect } from 'react';

const HeatConductionSimulator = () => {
  // Material presets with thermal diffusivity (m²/s)
  const materials = {
    'Iron (Pure)': 2.3e-5,
    'Steel - Carbon (AISI 1020)': 1.172e-5,
    'Steel - Stainless (304)': 4.2e-6,
    'Steel - Stainless (316)': 3.9e-6,
    'Steel - Tool (AISI D2)': 7.0e-6,
    'Steel - High Speed (M2)': 5.5e-6,
    'Aluminum - Pure': 9.7e-5,
    'Aluminum - Alloy (2024)': 6.8e-5,
    'Aluminum - Alloy (6061)': 6.4e-5,
    'Aluminum - Alloy (7075)': 4.8e-5,
    'Copper - Pure': 1.11e-4,
    'Copper - Brass (70/30)': 3.4e-5,
    'Copper - Bronze': 2.6e-5,
    'Titanium (Grade 5)': 3.2e-6,
    'Nickel': 2.3e-5,
    'Zinc': 4.1e-5,
    'Lead': 2.4e-5,
    'Silver': 1.71e-4,
    'Gold': 1.27e-4,
    'Tungsten': 6.8e-5,
    'Custom': 0
  };

  // Simulation parameters
  const [material, setMaterial] = useState('Iron (Pure)');
  const [customAlpha, setCustomAlpha] = useState('2.3e-5');
  const [length, setLength] = useState(1.0);
  const [nx, setNx] = useState(50);
  const [T0, setT0] = useState(100);
  const [TLeft, setTLeft] = useState(0);
  const [TRight, setTRight] = useState(0);
  const [isRunning, setIsRunning] = useState(false);
  const [time, setTime] = useState(0);
  const [temperatures, setTemperatures] = useState([]);
  const [heatmapData, setHeatmapData] = useState([]);
  const [probePosition, setProbePosition] = useState(null);
  const [heatmapProbePosition, setHeatmapProbePosition] = useState(null);

  // Get current alpha value
  const alpha = material === 'Custom' ? parseFloat(customAlpha) : materials[material];

  // Initialize simulation
  useEffect(() => {
    resetSimulation();
  }, [length, nx, T0, TLeft, TRight, material, customAlpha]);

  const resetSimulation = () => {
    const dx = length / (nx - 1);
    const currentAlpha = material === 'Custom' ? parseFloat(customAlpha) : materials[material];
    
    if (!currentAlpha || currentAlpha <= 0) return;

    const T = new Array(nx).fill(T0);
    T[0] = TLeft;
    T[nx - 1] = TRight;

    setTemperatures(T);
    setTime(0);
    setIsRunning(false);
    setHeatmapData([T]);
  };

  const stepSimulation = () => {
    const dx = length / (nx - 1);
    const currentAlpha = material === 'Custom' ? parseFloat(customAlpha) : materials[material];
    const dt = 0.4 * (dx * dx) / (2 * currentAlpha);
    const r = currentAlpha * dt / (dx * dx);

    const T = [...temperatures];
    const Tnew = new Array(nx);

    Tnew[0] = TLeft;
    Tnew[nx - 1] = TRight;

    for (let i = 1; i < nx - 1; i++) {
      Tnew[i] = T[i] + r * (T[i + 1] - 2 * T[i] + T[i - 1]);
    }

    setTemperatures(Tnew);
    setTime(prev => prev + dt);
    setHeatmapData(prev => {
      const updated = [...prev, Tnew];
      return updated.slice(-100);
    });
  };

  useEffect(() => {
    if (!isRunning) return;
    const interval = setInterval(() => {
      stepSimulation();
    }, 50);
    return () => clearInterval(interval);
  }, [isRunning, temperatures, nx, length, material, customAlpha]);

  const avgTemp = temperatures.reduce((a, b) => a + b, 0) / temperatures.length;
  const maxGradient = Math.max(...temperatures.slice(1).map((t, i) => 
    Math.abs(t - temperatures[i])
  ));

  const xValues = Array.from({ length: nx }, (_, i) => (i * length) / (nx - 1));

  const handleBarClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const ratio = x / rect.width;
    const position = Math.floor(ratio * nx);
    setProbePosition(Math.max(0, Math.min(nx - 1, position)));
  };

  const handleHeatmapClick = (e) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const ratio = x / rect.width;
    const position = Math.floor(ratio * nx);
    setHeatmapProbePosition(Math.max(0, Math.min(nx - 1, position)));
  };

  const probeTemp = probePosition !== null ? temperatures[probePosition] : null;
  const probeX = probePosition !== null ? xValues[probePosition] : null;

  const heatmapProbeTemp = heatmapProbePosition !== null && heatmapData.length > 0 
    ? heatmapData[heatmapData.length - 1][heatmapProbePosition] 
    : null;
  const heatmapProbeX = heatmapProbePosition !== null ? xValues[heatmapProbePosition] : null;

  // Format time
  const formatTime = (seconds) => {
    const hrs = Math.floor(seconds / 3600);
    const mins = Math.floor((seconds % 3600) / 60);
    const secs = (seconds % 60).toFixed(3);
    return `${secs}s | ${mins}m | ${hrs}h`;
  };

  return (
    <div style={{
      fontFamily: 'Arial, sans-serif',
      backgroundColor: '#C0C0C0',
      minHeight: '100vh',
      padding: '10px'
    }}>
      {/* Header */}
      <table width="100%" cellPadding="0" cellSpacing="0" border="0" style={{
        backgroundColor: '#000080',
        marginBottom: '10px'
      }}>
        <tbody>
          <tr>
            <td style={{ padding: '10px' }}>
              <font color="#FFFFFF" size="6"><b>1D Heat Conduction Simulator</b></font>
              <br />
              <font color="#FFFF00" size="3">Finite Difference Method for Transient Heat Transfer</font>
            </td>
          </tr>
        </tbody>
      </table>

      {/* Theory Section */}
      <table width="100%" cellPadding="10" cellSpacing="2" border="1" style={{
        backgroundColor: '#FFFFFF',
        borderColor: '#808080',
        marginBottom: '10px'
      }}>
        <tbody>
          <tr>
            <td bgcolor="#008080">
              <font color="#FFFFFF" size="4"><b>Mathematical Theory</b></font>
            </td>
          </tr>
          <tr>
            <td>
              <p><b>1. The Heat Equation (Fourier's Law)</b></p>
              <p>The one-dimensional transient heat conduction is governed by:</p>
              <p style={{ fontFamily: 'Courier New', backgroundColor: '#FFFFCC', padding: '10px', border: '1px solid black' }}>
                ∂T/∂t = α · ∂²T/∂x²
              </p>
              <p>Where:</p>
              <ul>
                <li><b>T</b> = Temperature (°C)</li>
                <li><b>t</b> = Time (s)</li>
                <li><b>x</b> = Spatial coordinate (m)</li>
                <li><b>α</b> = Thermal diffusivity (m²/s), defined as α = k/(ρ·c<sub>p</sub>)</li>
              </ul>

              <p><b>2. Finite Difference Discretization (Explicit Euler Method)</b></p>
              <p>Using forward difference in time and central difference in space:</p>
              <p style={{ fontFamily: 'Courier New', backgroundColor: '#FFFFCC', padding: '10px', border: '1px solid black' }}>
                T<sub>i</sub><sup>n+1</sup> = T<sub>i</sub><sup>n</sup> + r · [T<sub>i+1</sub><sup>n</sup> - 2·T<sub>i</sub><sup>n</sup> + T<sub>i-1</sub><sup>n</sup>]
              </p>
              <p>Where r = α·Δt/Δx² is the mesh Fourier number</p>

              <p><b>3. CFL Stability Condition</b></p>
              <p>For numerical stability, the time step must satisfy:</p>
              <p style={{ fontFamily: 'Courier New', backgroundColor: '#FFFFCC', padding: '10px', border: '1px solid black' }}>
                Δt ≤ Δx² / (2α)
              </p>
              <p>This ensures that r ≤ 0.5, preventing numerical oscillations and instability.</p>

              <p><b>4. Boundary Conditions</b></p>
              <p>Dirichlet (fixed temperature) conditions are applied at both ends:</p>
              <ul>
                <li>T(x=0, t) = T<sub>left</sub></li>
                <li>T(x=L, t) = T<sub>right</sub></li>
              </ul>
            </td>
          </tr>
        </tbody>
      </table>

      {/* Main Content */}
      <table width="100%" cellPadding="0" cellSpacing="10" border="0">
        <tbody>
          <tr>
            <td width="30%" valign="top">
              {/* Control Panel */}
              <table width="100%" cellPadding="10" cellSpacing="2" border="1" style={{
                backgroundColor: '#FFFFFF',
                borderColor: '#808080'
              }}>
                <tbody>
                  <tr>
                    <td bgcolor="#800000">
                      <font color="#FFFFFF" size="4"><b>Control Panel</b></font>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <p><b>Material Selection:</b></p>
                      <select 
                        value={material} 
                        onChange={(e) => setMaterial(e.target.value)}
                        disabled={isRunning}
                        style={{ width: '100%', padding: '5px', fontSize: '14px' }}
                      >
                        {Object.keys(materials).map(mat => (
                          <option key={mat} value={mat}>{mat}</option>
                        ))}
                      </select>
                      
                      {material === 'Custom' && (
                        <div style={{ marginTop: '10px' }}>
                          <p><b>Custom α (m²/s):</b></p>
                          <input
                            type="text"
                            value={customAlpha}
                            onChange={(e) => setCustomAlpha(e.target.value)}
                            disabled={isRunning}
                            style={{ width: '100%', padding: '5px', fontSize: '14px' }}
                          />
                        </div>
                      )}
                      
                      <p style={{ backgroundColor: '#FFFFE0', padding: '5px', marginTop: '10px', border: '1px solid black' }}>
                        <font size="2">α = {alpha ? alpha.toExponential(2) : 'Invalid'} m²/s</font>
                      </p>

                      <hr />

                      <p><b>Bar Length (m):</b> {length.toFixed(1)}</p>
                      <input
                        type="range"
                        min="0.1"
                        max="2"
                        step="0.1"
                        value={length}
                        onChange={(e) => setLength(parseFloat(e.target.value))}
                        disabled={isRunning}
                        style={{ width: '100%' }}
                      />

                      <p><b>Initial Temperature (°C):</b> {T0}</p>
                      <input
                        type="range"
                        min="0"
                        max="200"
                        step="10"
                        value={T0}
                        onChange={(e) => setT0(parseInt(e.target.value))}
                        disabled={isRunning}
                        style={{ width: '100%' }}
                      />

                      <p><b>Left Boundary (°C):</b> {TLeft}</p>
                      <input
                        type="range"
                        min="0"
                        max="200"
                        step="10"
                        value={TLeft}
                        onChange={(e) => setTLeft(parseInt(e.target.value))}
                        disabled={isRunning}
                        style={{ width: '100%' }}
                      />

                      <p><b>Right Boundary (°C):</b> {TRight}</p>
                      <input
                        type="range"
                        min="0"
                        max="200"
                        step="10"
                        value={TRight}
                        onChange={(e) => setTRight(parseInt(e.target.value))}
                        disabled={isRunning}
                        style={{ width: '100%' }}
                      />

                      <hr />

                      <center>
                        <button
                          onClick={() => setIsRunning(!isRunning)}
                          style={{
                            padding: '10px 20px',
                            fontSize: '16px',
                            backgroundColor: isRunning ? '#FF0000' : '#00FF00',
                            border: '2px outset',
                            cursor: 'pointer',
                            width: '48%',
                            marginRight: '4%'
                          }}
                        >
                          {isRunning ? 'PAUSE' : 'START'}
                        </button>
                        <button
                          onClick={resetSimulation}
                          style={{
                            padding: '10px 20px',
                            fontSize: '16px',
                            backgroundColor: '#FFFF00',
                            border: '2px outset',
                            cursor: 'pointer',
                            width: '48%'
                          }}
                        >
                          RESET
                        </button>
                      </center>
                    </td>
                  </tr>
                </tbody>
              </table>

              {/* Metrics */}
              <table width="100%" cellPadding="10" cellSpacing="2" border="1" style={{
                backgroundColor: '#FFFFFF',
                borderColor: '#808080',
                marginTop: '10px'
              }}>
                <tbody>
                  <tr>
                    <td bgcolor="#000080">
                      <font color="#FFFFFF" size="4"><b>Metrics</b></font>
                    </td>
                  </tr>
                  <tr>
                    <td>
                      <table width="100%" cellPadding="5">
                        <tbody>
                          <tr>
                            <td bgcolor="#FFFFCC">
                              <b>Simulation Time:</b><br />
                              <font size="4" color="#FF0000">{formatTime(time)}</font>
                            </td>
                          </tr>
                          <tr>
                            <td bgcolor="#FFCCCC">
                              <b>Average Temperature:</b><br />
                              <font size="5" color="#0000FF">{avgTemp.toFixed(2)} °C</font>
                            </td>
                          </tr>
                          <tr>
                            <td bgcolor="#CCFFCC">
                              <b>Max Gradient:</b><br />
                              <font size="5" color="#008000">{maxGradient.toFixed(2)} °C</font>
                            </td>
                          </tr>
                          {probePosition !== null && (
                            <tr>
                              <td bgcolor="#CCCCFF">
                                <b>Profile Probe:</b><br />
                                <font size="4" color="#800080">
                                  Position: {probeX?.toFixed(3)} m<br />
                                  Temp: {probeTemp?.toFixed(2)} °C
                                </font>
                              </td>
                            </tr>
                          )}
                          {heatmapProbePosition !== null && (
                            <tr>
                              <td bgcolor="#FFCCFF">
                                <b>Heatmap Probe:</b><br />
                                <font size="4" color="#FF00FF">
                                  Position: {heatmapProbeX?.toFixed(3)} m<br />
                                  Temp: {heatmapProbeTemp?.toFixed(2)} °C
                                </font>
                              </td>
                            </tr>
                          )}
                        </tbody>
                      </table>
                    </td>
                  </tr>
                </tbody>
              </table>
            </td>

            <td width="70%" valign="top">
              {/* Visualizations */}
              <table width="100%" cellPadding="10" cellSpacing="2" border="1" style={{
                backgroundColor: '#FFFFFF',
                borderColor: '#808080',
                marginBottom: '10px'
              }}>
                <tbody>
                  <tr>
                    <td bgcolor="#008000">
                      <font color="#FFFFFF" size="4"><b>Heat Distribution Over Time</b></font>
                    </td>
                  </tr>
                  <tr>
                    <td align="center">
                      <div onClick={handleHeatmapClick} style={{ cursor: 'crosshair' }}>
                        <HeatmapPlot 
                          data={heatmapData} 
                          xValues={xValues} 
                          probePosition={heatmapProbePosition}
                        />
                      </div>
                      <p style={{ backgroundColor: '#FFFFCC', padding: '5px', marginTop: '10px', border: '1px dashed black' }}>
                        <b>Click on the heatmap to place a temperature probe!</b>
                      </p>
                    </td>
                  </tr>
                </tbody>
              </table>

              <table width="100%" cellPadding="10" cellSpacing="2" border="1" style={{
                backgroundColor: '#FFFFFF',
                borderColor: '#808080'
              }}>
                <tbody>
                  <tr>
                    <td bgcolor="#800080">
                      <font color="#FFFFFF" size="4"><b>Current Temperature Profile</b></font>
                    </td>
                  </tr>
                  <tr>
                    <td align="center">
                      <div onClick={handleBarClick} style={{ cursor: 'crosshair' }}>
                        <LineChart 
                          temperatures={temperatures} 
                          xValues={xValues} 
                          probePosition={probePosition}
                        />
                      </div>
                      <p style={{ backgroundColor: '#FFFFCC', padding: '5px', marginTop: '10px', border: '1px dashed black' }}>
                        <b>Click on the chart to place a temperature probe!</b>
                      </p>
                    </td>
                  </tr>
                </tbody>
              </table>
            </td>
          </tr>
        </tbody>
      </table>

      {/* Footer */}
      <center style={{ marginTop: '20px' }}>
        <font size="2" color="#000080">
          <b>Heat Conduction Simulator v3.0 "Heat 3"</b><br />
          Powered by Finite Difference Method | © 2005 Style Tribute
        </font>
      </center>
    </div>
  );
};

const HeatmapPlot = ({ data, xValues, probePosition }) => {
  if (data.length === 0) return <div style={{ padding: '50px', backgroundColor: '#E0E0E0', border: '2px inset' }}>Initializing...</div>;

  const canvas = React.useRef(null);

  useEffect(() => {
    if (!canvas.current || data.length === 0) return;

    const ctx = canvas.current.getContext('2d');
    const width = canvas.current.width;
    const height = canvas.current.height;

    ctx.clearRect(0, 0, width, height);

    const maxT = Math.max(...data.flat());
    const minT = Math.min(...data.flat());

    const cellWidth = width / data[0].length;
    const cellHeight = height / data.length;

    data.forEach((row, rowIdx) => {
      row.forEach((temp, colIdx) => {
        const normalized = (temp - minT) / (maxT - minT || 1);
        const r = Math.floor(normalized * 255);
        const b = Math.floor((1 - normalized) * 255);
        ctx.fillStyle = `rgb(${r}, 0, ${b})`;
        ctx.fillRect(colIdx * cellWidth, rowIdx * cellHeight, cellWidth, cellHeight);
      });
    });

    // Draw grid
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 1;
    for (let i = 0; i <= data[0].length; i += 5) {
      ctx.beginPath();
      ctx.moveTo(i * cellWidth, 0);
      ctx.lineTo(i * cellWidth, height);
      ctx.stroke();
    }

    // Draw probe marker as vertical line
    if (probePosition !== null) {
      const x = (probePosition / data[0].length) * width;
      
      ctx.strokeStyle = '#FFFF00';
      ctx.lineWidth = 3;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();

      ctx.strokeStyle = '#000000';
      ctx.lineWidth = 1;
      ctx.beginPath();
      ctx.moveTo(x, 0);
      ctx.lineTo(x, height);
      ctx.stroke();
    }

  }, [data, probePosition]);

  return (
    <div>
      <canvas 
        ref={canvas} 
        width={600} 
        height={250} 
        style={{ 
          border: '2px solid black',
          backgroundColor: '#FFFFFF'
        }} 
      />
      <table width="600" cellPadding="5" style={{ marginTop: '5px' }}>
        <tbody>
          <tr>
            <td align="left"><font size="2">← Beginning of Rod</font></td>
            <td align="center"><font size="2"><b>Time Progress (Downward) →</b></font></td>
            <td align="right"><font size="2">End of Rod →</font></td>
          </tr>
        </tbody>
      </table>
    </div>
  );
};

const LineChart = ({ temperatures, xValues, probePosition }) => {
  const canvas = React.useRef(null);

  useEffect(() => {
    if (!canvas.current || temperatures.length === 0) return;

    const ctx = canvas.current.getContext('2d');
    const width = canvas.current.width;
    const height = canvas.current.height;
    const padding = 60;

    ctx.clearRect(0, 0, width, height);
    ctx.fillStyle = '#FFFFFF';
    ctx.fillRect(0, 0, width, height);

    const maxT = Math.max(...temperatures, 1);
    const minT = Math.min(...temperatures, 0);
    const maxX = Math.max(...xValues);

    // Draw axes
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = 2;
    ctx.beginPath();
    ctx.moveTo(padding, padding);
    ctx.lineTo(padding, height - padding);
    ctx.lineTo(width - padding, height - padding);
    ctx.stroke();

    // Draw labels
    ctx.fillStyle = '#000000';
    ctx.font = '14px Arial';
    ctx.fillText('Temperature (°C)', 10, 30);
    ctx.fillText('Position (m)', width / 2 - 40, height - 10);

    // Draw grid
    ctx.strokeStyle = '#CCCCCC';
    ctx.lineWidth = 1;
    for (let i = 0; i <= 5; i++) {
      const y = padding + (i / 5) * (height - 2 * padding);
      ctx.beginPath();
      ctx.moveTo(padding, y);
      ctx.lineTo(width - padding, y);
      ctx.stroke();
    }

    // Draw temperature line
    ctx.strokeStyle = '#FF0000';
    ctx.lineWidth = 3;
    ctx.beginPath();

    temperatures.forEach((temp, i) => {
      const x = padding + ((xValues[i] / maxX) * (width - 2 * padding));
      const y = height - padding - ((temp - minT) / (maxT - minT || 1)) * (height - 2 * padding);

      if (i === 0) ctx.moveTo(x, y);
      else ctx.lineTo(x, y);
    });

    ctx.stroke();

    // Draw probe marker
    if (probePosition !== null) {
      const x = padding + ((xValues[probePosition] / maxX) * (width - 2 * padding));
      const y = height - padding - ((temperatures[probePosition] - minT) / (maxT - minT || 1)) * (height - 2 * padding);
      
      ctx.fillStyle = '#0000FF';
      ctx.beginPath();
      ctx.arc(x, y, 8, 0, 2 * Math.PI);
      ctx.fill();
      ctx.strokeStyle = '#FFFF00';
      ctx.lineWidth = 2;
      ctx.stroke();
    }

    // Draw tick marks
    ctx.fillStyle = '#000000';
    ctx.font = '12px Arial';
    for (let i = 0; i <= 5; i++) {
      const temp = minT + (i / 5) * (maxT - minT);
      const y = height - padding - (i / 5) * (height - 2 * padding);
      ctx.fillText(temp.toFixed(0), 10, y + 4);

      const x = padding + (i / 5) * (width - 2 * padding);
      const pos = (i / 5) * maxX;
      ctx.fillText(pos.toFixed(2), x - 15, height - padding + 20);
    }

  }, [temperatures, xValues, probePosition]);

  return (
    <canvas 
      ref={canvas} 
      width={600} 
      height={300} 
      style={{ 
        border: '2px solid black',
        backgroundColor: '#FFFFFF'
      }} 
    />
  );
};

export default HeatConductionSimulator;
