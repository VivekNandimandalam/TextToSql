import React, { useState, useEffect } from 'react';
import { useLocation } from 'react-router-dom';
import Navbar from './Navbar';
import io from 'socket.io-client';
import './MigrationStatus.css';

// Ensure the backend WebSocket address matches your backend address and port
const socket = io.connect('http://127.0.0.1:5000', {
  transports: ['websocket'],
});


function MigrationStatus() {
  const location = useLocation();
  const { selectedObjects, loggedInUser } = location.state || {};
  const [migrationStatus, setMigrationStatus] = useState({});

  useEffect(() => {
    if (selectedObjects) {
      // Emit event to start migration when the component is mounted
      socket.emit('start_migration', selectedObjects);
    }

    // Listen for 'migration_status' events from the backend
    socket.on('migration_status', (data) => {
      console.log("Received migration status:", data); // Check if the frontend receives the data
      // Update the migrationStatus state with new data from the backend
      setMigrationStatus((prevStatus) => ({ ...prevStatus, ...data }));
    });

    // Cleanup the socket listener when the component unmounts
    return () => {
      socket.off('migration_status');
    };
  }, [selectedObjects]);

  return (
    <div className="migration-status-container">
      <Navbar loggedInUser={loggedInUser} /> {/* Display the logged-in user in the Navbar */}

      <div className="status-content">
        <h2>Migration Status</h2>
        <h4>Logged in as: {loggedInUser}</h4>

        <div className="status-section">
          <h3>Tables</h3>
          <ul>
            {selectedObjects?.tables && selectedObjects.tables.map((table, index) => (
              <li key={index}>
                {table}: {migrationStatus[table] || 'Waiting...'}
              </li>
            ))}
          </ul>
        </div>

        <div className="status-section">
          <h3>Views</h3>
          <ul>
            {selectedObjects?.views && selectedObjects.views.map((view, index) => (
              <li key={index}>
                {view}: {migrationStatus[view] || 'Waiting...'}
              </li>
            ))}
          </ul>
        </div>

        <div className="status-section">
          <h3>Stored Procedures</h3>
          <ul>
            {selectedObjects?.stored_procedures && selectedObjects.stored_procedures.map((proc, index) => (
              <li key={index}>
                {proc}: {migrationStatus[proc] || 'Waiting...'}
              </li>
            ))}
          </ul>
        </div>
      </div>
    </div>
  );
}

export default MigrationStatus;
