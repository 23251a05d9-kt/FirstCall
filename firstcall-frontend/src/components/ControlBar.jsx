import { useRef } from "react";

const ControlBar = ({
  cameraId,
  setCameraId,
  handleVideoUpload,
  startMonitoring,
  systemState,
}) => {
  const fileInputRef = useRef(null);

  return (
    <div className="relative bg-gradient-to-r from-[#0E1422] via-[#111827] to-[#0E1422] border-t border-purple-800/30 backdrop-blur-xl p-6">

      {/* Subtle top glow */}
      <div className="absolute -top-[1px] left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-purple-600 to-transparent opacity-40"></div>

      <div className="max-w-6xl mx-auto flex items-center justify-between gap-6">

        {/* Camera Input */}
        <div className="flex flex-col">
          <label className="text-xs text-purple-400 mb-1 tracking-widest uppercase">
            Camera ID
          </label>
          <input
            type="text"
            placeholder="CAM1"
            value={cameraId}
            onChange={(e) => setCameraId(e.target.value)}
            className="bg-[#0B0F19] text-white px-4 py-2 rounded-lg border border-purple-700/40 focus:border-purple-500 focus:ring-1 focus:ring-purple-500 outline-none transition shadow-inner shadow-purple-900/20"
          />
        </div>

        {/* Upload Button */}
        <div className="flex flex-col">
          <label className="text-xs text-blue-400 mb-1 tracking-widest uppercase">
            Upload Footage
          </label>

          <button
            onClick={() => fileInputRef.current.click()}
            className="px-5 py-2 rounded-lg bg-gradient-to-r from-blue-600 to-purple-600 hover:opacity-90 transition shadow-[0_0_20px_rgba(99,102,241,0.4)]"
          >
            Select Video
          </button>

          <input
            type="file"
            accept="video/*"
            ref={fileInputRef}
            onChange={handleVideoUpload}
            className="hidden"
          />
        </div>

        {/* Start Button */}
        <div className="flex flex-col">
          <label className="text-xs text-green-400 mb-1 tracking-widest uppercase">
            System Control
          </label>

          <button
            onClick={startMonitoring}
            disabled={systemState === "MONITORING"}
            className={`px-8 py-2 rounded-lg font-semibold tracking-wide transition-all duration-300 ${
              systemState === "MONITORING"
                ? "bg-gray-700 cursor-not-allowed"
                : "bg-gradient-to-r from-purple-600 to-blue-600 hover:scale-105 hover:shadow-[0_0_25px_rgba(124,58,237,0.6)]"
            }`}
          >
            {systemState === "MONITORING"
              ? "Monitoring..."
              : "Start Monitoring"}
          </button>
        </div>

      </div>
    </div>
  );
};

export default ControlBar;
