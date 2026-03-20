import { useRef, useEffect } from "react";

const VideoPanel = ({ videoURL, systemState, onVideoEnd }) => {
  const videoRef = useRef(null);

useEffect(() => {
  if (systemState === "MONITORING" && videoRef.current) {
    videoRef.current.play().catch(() => {});
  }
}, [systemState]);


  const getBorder = () => {
    switch (systemState) {
      case "ANALYZING":
        return "border-purple-500 shadow-[0_0_30px_#A855F7]";
      case "MONITORING":
        return "border-blue-500 shadow-[0_0_25px_#3B82F6]";
      case "DETECTED":
        return "border-red-500 shadow-[0_0_30px_#EF4444]";
      case "CALLING":
        return "border-orange-400 shadow-[0_0_30px_#FB923C]";
      case "ALERT_SENT":
        return "border-green-500 shadow-[0_0_30px_#22C55E]";
      default:
        return "border-gray-800";
    }
  };

  return (
    <div className="flex-[3] bg-gradient-to-br from-[#111827] to-[#0E1422] rounded-2xl p-4 border border-gray-800">
      <h2 className="text-lg text-blue-400 mb-4">Live CCTV Feed</h2>

      <div
        className={`bg-black h-[420px] rounded-xl border-2 transition-all duration-500 flex items-center justify-center overflow-hidden ${getBorder()}`}
      >
        {videoURL ? (
          <video
            ref={videoRef}
            src={videoURL}
            muted
            playsInline
            className="w-full h-full object-contain"
            onEnded={onVideoEnd}
          />
        ) : (
          <span className="text-gray-500">No video uploaded</span>
        )}
      </div>
    </div>
  );
};

export default VideoPanel;
