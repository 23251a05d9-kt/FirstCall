const EventLog = ({ logs }) => {
  return (
    <div className="bg-[#0E1422] border border-gray-800 rounded-xl p-4 h-40 overflow-y-auto text-sm text-gray-400">
      {logs.length === 0 ? (
        <p>No events yet...</p>
      ) : (
        logs.map((log, index) => (
          <p key={index}>[{log.time}] {log.message}</p>
        ))
      )}
    </div>
  );
};

export default EventLog;
