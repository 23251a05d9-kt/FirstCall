const InfoPanel = ({ cameraId, incidentType, systemState }) => {
  return (
    <div className="flex-[2] bg-[#111827] rounded-xl p-4 flex flex-col gap-6">
      
      <div>
        <h2 className="text-lg text-blue-400 mb-2">Camera Info</h2>
        <p className="text-sm text-gray-400">
          Camera ID: {cameraId || "-"}
        </p>
      </div>

      <div>
        <h2 className="text-lg text-blue-400 mb-2">Incident</h2>
        <p className="text-sm text-gray-400">
          Type: {incidentType || "None"}
        </p>
      </div>

      <div>
        <h2 className="text-lg text-blue-400 mb-2">Alert Status</h2>
        <p className="text-sm text-gray-400">
          {systemState === "IDLE" && "Waiting to start..."}
          {systemState === "MONITORING" && "Scanning video..."}
          {systemState === "DETECTED" && "Incident detected!"}
          {systemState === "CALLING" && "Calling authorities..."}
          {systemState === "ALERT_SENT" && "Alert successfully sent."}
          {systemState === "COMPLETED" && "Monitoring completed."}
        </p>
      </div>

    </div>
  );
};

export default InfoPanel;
