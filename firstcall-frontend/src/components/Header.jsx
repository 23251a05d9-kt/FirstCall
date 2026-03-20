const Header = ({ systemState }) => {
  const getStatusColor = () => {
    switch (systemState) {
      case "MONITORING":
        return "bg-blue-500/20 text-blue-400 border-blue-500";
      case "DETECTED":
        return "bg-red-500/20 text-red-400 border-red-500 animate-pulse";
      case "CALLING":
        return "bg-orange-500/20 text-orange-400 border-orange-400";
      case "ALERT_SENT":
        return "bg-green-500/20 text-green-400 border-green-500";
      default:
        return "bg-gray-500/20 text-gray-400 border-gray-500";
    }
  };

  return (
    <header className="h-16 border-b border-gray-800 flex items-center justify-between px-6 backdrop-blur-lg bg-[#0E1422]/60">

      <div className="flex items-center gap-3">
        
        {/* Minimal Logo */}
        <div className="relative w-9 h-9 flex items-center justify-center">

  {/* Outer Ring */}
  <div className="absolute w-9 h-9 rounded-full border border-purple-500/40"></div>

  {/* Rotating Sweep Line */}
  <div className="absolute w-9 h-9 rounded-full border-t-2 border-purple-400 animate-spin-slow"></div>

  {/* Inner Glow Dot */}
  <div className="w-3 h-3 bg-gradient-to-r from-purple-400 to-blue-400 rounded-full shadow-[0_0_10px_#7C3AED]"></div>

</div>

        <h1
          className="text-2xl tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400"
          style={{ fontFamily: "Orbitron, sans-serif" }}
        >
          FIRSTCALL
        </h1>
      </div>

      <div className={`px-4 py-1 rounded-full border text-sm font-semibold ${getStatusColor()}`}>
        {systemState}
      </div>
    </header>
  );
};

export default Header;
