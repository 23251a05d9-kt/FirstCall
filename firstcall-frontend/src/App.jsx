import { useEffect, useState, useRef } from "react";
import axios from "axios";
import SplashScreen from "./components/SplashScreen";
import Header from "./components/Header";
import VideoPanel from "./components/VideoPanel";
import InfoPanel from "./components/InfoPanel";
import ControlBar from "./components/ControlBar";
import EventLog from "./components/EventLog";

function App() {

  const alertAudioRef = useRef(null);

  // Splash
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    const timer = setTimeout(() => setLoading(false), 2000);
    return () => clearTimeout(timer);
  }, []);

  // Main State
  const [cameraId, setCameraId] = useState("");
  const [videoFile, setVideoFile] = useState(null);
  const [videoURL, setVideoURL] = useState(null);
  const [systemState, setSystemState] = useState("IDLE");
  const [incidentType, setIncidentType] = useState(null);
  const [logs, setLogs] = useState([]);

  const pollingRef = useRef(null);
  const alertPlayedRef = useRef(false);

  const addLog = (message) => {
    const time = new Date().toLocaleTimeString();
    setLogs((prev) => [...prev, { time, message }]);
  };

  // Upload Handler
  const handleVideoUpload = (e) => {
    const file = e.target.files[0];
    if (file) {
      setVideoFile(file);
      setVideoURL(URL.createObjectURL(file));
      addLog("Video uploaded.");
    }
  };

  // Start Monitoring
  const startMonitoring = async () => {
    if (!cameraId || !videoFile) {
      alert("Enter Camera ID and upload video.");
      return;
    }

    if (pollingRef.current) {
      clearInterval(pollingRef.current);
    }

    setSystemState("MONITORING");
    alertPlayedRef.current = false;

    // 🔓 Unlock browser audio policy
    if (alertAudioRef.current) {
      alertAudioRef.current.play()
        .then(() => {
          alertAudioRef.current.pause();
          alertAudioRef.current.currentTime = 0;
        })
        .catch(() => {});
    }

    const formData = new FormData();
    formData.append("camera_id", cameraId);
    formData.append("video", videoFile);

    try {
      await axios.post("http://127.0.0.1:8000/start-monitoring", formData);
      addLog("Monitoring started.");
      startPolling();
    } catch (error) {
      console.error(error);
      alert("Backend connection failed.");
    }
  };

  // Polling
  const startPolling = () => {
    pollingRef.current = setInterval(async () => {
      try {
        const res = await axios.get("http://127.0.0.1:8000/status");
        const data = res.data;

        setSystemState(data.state);
        setIncidentType(data.incident_type);

        if (data.state === "DETECTED" && !alertPlayedRef.current) {
          addLog(`Incident detected: ${data.incident_type}`);
          playAlertSound();
          alertPlayedRef.current = true;
        }

        if (data.state === "ALERT_SENT") {
          addLog("Alert successfully sent.");
          clearInterval(pollingRef.current);
        }

      } catch (err) {
        console.error("Polling error:", err);
      }
    }, 2000);
  };

  // Proper Alert Sound
  const playAlertSound = () => {
    if (alertAudioRef.current) {
      alertAudioRef.current.currentTime = 0;
      alertAudioRef.current.play().catch(() => {});
    }
  };

  if (loading) return <SplashScreen />;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#050816] via-[#0B0F19] to-[#0E1422] text-white flex flex-col relative overflow-hidden">

      <Header systemState={systemState} />

      <main className="flex flex-1 p-6 gap-6 relative z-10">

        <VideoPanel
          videoURL={videoURL}
          systemState={systemState}
          onVideoEnd={() => {
            if (incidentType === "NORMAL") {
              setSystemState("COMPLETED");
              addLog("No incidents detected.");
            } else {
              addLog("Video playback completed.");
            }
          }}
        />

        <div className="flex flex-col gap-6 flex-[2]">
          <InfoPanel
            cameraId={cameraId}
            incidentType={incidentType}
            systemState={systemState}
          />
          <EventLog logs={logs} />
        </div>

      </main>

      <ControlBar
        cameraId={cameraId}
        setCameraId={setCameraId}
        handleVideoUpload={handleVideoUpload}
        startMonitoring={startMonitoring}
        systemState={systemState}
      />

      {/* Hidden Audio Element */}
      <audio ref={alertAudioRef} src="/alert.mp3" preload="auto" />

    </div>
  );
}

export default App;
