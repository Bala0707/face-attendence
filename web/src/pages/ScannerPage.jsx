import React, { useState, useRef, useEffect } from 'react';
import { Camera, Volume2, VolumeX, Play, Square, CheckCircle2, AlertCircle, Sparkles } from 'lucide-react';
import { recognizeFrameApi } from '../services/api';

export default function ScannerPage({ onMarkAttendance }) {
  const [isScanning, setIsScanning] = useState(false);
  const [enableSound, setEnableSound] = useState(true);
  const [statusMessage, setStatusMessage] = useState('Scanner Ready - Click Start Camera Scanner to begin');
  const [statusType, setStatusType] = useState('idle');
  const [detectedFaces, setDetectedFaces] = useState([]);

  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const scanIntervalRef = useRef(null);

  useEffect(() => {
    return () => {
      stopCamera();
    };
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ video: { width: 640, height: 480 } });
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        await videoRef.current.play();
      }
      setIsScanning(true);
      setStatusMessage('🟢 Live OpenCV AI Scanning Active...');
      setStatusType('active');

      // Start recognition frame loop
      scanIntervalRef.current = setInterval(processFrame, 600);
    } catch (err) {
      console.error('Camera access error:', err);
      setStatusMessage('⚠️ Unable to access camera. Check browser permissions.');
      setStatusType('error');
    }
  };

  const stopCamera = () => {
    if (scanIntervalRef.current) {
      clearInterval(scanIntervalRef.current);
      scanIntervalRef.current = null;
    }
    if (videoRef.current && videoRef.current.srcObject) {
      const tracks = videoRef.current.srcObject.getTracks();
      tracks.forEach(track => track.stop());
      videoRef.current.srcObject = null;
    }
    setIsScanning(false);
    setDetectedFaces([]);
    setStatusMessage('⏹ Scanner Stopped');
    setStatusType('idle');
  };

  const processFrame = async () => {
    if (!videoRef.current || !videoRef.current.videoWidth) return;

    // Create temporary offscreen canvas to extract frame
    const tempCanvas = document.createElement('canvas');
    tempCanvas.width = videoRef.current.videoWidth;
    tempCanvas.height = videoRef.current.videoHeight;
    const ctx = tempCanvas.getContext('2d');
    ctx.drawImage(videoRef.current, 0, 0);

    const base64Img = tempCanvas.toDataURL('image/jpeg', 0.7);
    const res = await recognizeFrameApi(base64Img);

    if (res && res.faces) {
      setDetectedFaces(res.faces);

      // Check if attendance was newly marked
      const newlyMarked = res.faces.find(f => f.attendance_marked);
      if (newlyMarked) {
        setStatusMessage(`✅ Attendance Marked: ${newlyMarked.name} (${newlyMarked.status})`);
        setStatusType('success');
        if (onMarkAttendance) {
          onMarkAttendance(newlyMarked.person_id, newlyMarked.name, newlyMarked.confidence);
        }

        if (enableSound) {
          try {
            const audioCtx = new (window.AudioContext || window.webkitAudioContext)();
            const osc = audioCtx.createOscillator();
            osc.type = 'sine';
            osc.frequency.setValueAtTime(900, audioCtx.currentTime);
            osc.connect(audioCtx.destination);
            osc.start();
            osc.stop(audioCtx.currentTime + 0.2);
          } catch (e) {
            console.log('Beep audio', e);
          }
        }
      }
    }
  };

  return (
    <div className="space-y-6 pb-10">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-extrabold text-white tracking-tight">Live Camera Scanner</h2>
          <p className="text-xs text-slate-400">Real-time WebRTC camera stream connected with OpenCV Python detection & recognition</p>
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
        {/* CAMERA CANVAS VIEW (3 Cols) */}
        <div className="lg:col-span-3 glass-card rounded-2xl p-4 relative overflow-hidden bg-[#090A0F] border border-[#232740] flex flex-col justify-between min-h-[440px]">
          <div className="relative w-full h-[420px] rounded-xl overflow-hidden bg-slate-950 flex items-center justify-center">
            <video
              ref={videoRef}
              className={`w-full h-full object-cover ${isScanning ? 'block' : 'hidden'}`}
              playsInline
              muted
            />

            {/* Bounding Boxes Overlay */}
            {isScanning && detectedFaces.map((f, i) => {
              const [x, y, w, h] = f.bbox;
              // Map bbox to percentages for responsive video overlay
              const videoW = videoRef.current?.videoWidth || 640;
              const videoH = videoRef.current?.videoHeight || 480;

              const leftPct = (x / videoW) * 100;
              const topPct = (y / videoH) * 100;
              const widthPct = (w / videoW) * 100;
              const heightPct = (h / videoH) * 100;

              return (
                <div
                  key={i}
                  className={`absolute border-2 transition-all duration-150 ${
                    f.is_recognized ? 'border-emerald-400 bg-emerald-500/10' : 'border-amber-400 bg-amber-500/10'
                  }`}
                  style={{
                    left: `${leftPct}%`,
                    top: `${topPct}%`,
                    width: `${widthPct}%`,
                    height: `${heightPct}%`,
                  }}
                >
                  <div className={`absolute -top-7 left-0 px-2 py-0.5 text-[11px] font-bold rounded shadow ${
                    f.is_recognized ? 'bg-emerald-600 text-white' : 'bg-amber-600 text-white'
                  }`}>
                    {f.name} ({f.confidence}%)
                  </div>
                </div>
              );
            })}

            {!isScanning && (
              <div className="text-center space-y-3 p-6">
                <div className="w-16 h-16 rounded-full bg-slate-900/80 border border-slate-800 flex items-center justify-center mx-auto text-slate-400">
                  <Camera className="w-8 h-8" />
                </div>
                <h3 className="text-slate-300 font-semibold text-sm">[ Camera Stream Offline ]</h3>
                <p className="text-xs text-slate-500 max-w-sm mx-auto">Click "Start Camera Scanner" to launch real-time OpenCV face recognition scan.</p>
              </div>
            )}

            {/* Live HUD Overlay Badge */}
            {isScanning && (
              <div className="absolute top-4 left-4 px-3 py-1.5 rounded-full bg-slate-950/80 border border-emerald-500/30 text-emerald-400 text-xs font-mono font-bold flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
                <span>30 FPS | OPENCV AI ENGINE ACTIVE</span>
              </div>
            )}
          </div>
        </div>

        {/* CONTROLS SIDEBAR (1 Col) */}
        <div className="glass-card rounded-2xl p-6 space-y-6 flex flex-col justify-between">
          <div className="space-y-4">
            <h3 className="font-bold text-white text-base">Scanner Controls</h3>

            {/* Audio Toggle */}
            <div className="flex items-center justify-between p-3 rounded-xl bg-[#141724] border border-[#232740]">
              <div className="flex items-center gap-2 text-xs font-semibold text-slate-300">
                {enableSound ? <Volume2 className="w-4 h-4 text-emerald-400" /> : <VolumeX className="w-4 h-4 text-slate-400" />}
                <span>Audio Beep Alert</span>
              </div>
              <button
                onClick={() => setEnableSound(!enableSound)}
                className={`w-10 h-6 rounded-full transition-colors relative p-1 ${enableSound ? 'bg-emerald-600' : 'bg-slate-700'}`}
              >
                <div className={`w-4 h-4 rounded-full bg-white transition-transform ${enableSound ? 'translate-x-4' : 'translate-x-0'}`} />
              </button>
            </div>

            {/* Start / Stop Buttons */}
            {!isScanning ? (
              <button
                onClick={startCamera}
                className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl bg-gradient-to-r from-emerald-500 to-teal-600 text-white font-bold text-sm shadow-lg shadow-emerald-500/20 hover:brightness-110 transition-all"
              >
                <Play className="w-4 h-4 fill-white" />
                <span>Start Camera Scanner</span>
              </button>
            ) : (
              <button
                onClick={stopCamera}
                className="w-full flex items-center justify-center gap-2 py-3.5 rounded-xl bg-gradient-to-r from-rose-600 to-red-600 text-white font-bold text-sm shadow-lg shadow-rose-500/20 hover:brightness-110 transition-all"
              >
                <Square className="w-4 h-4 fill-white" />
                <span>Stop Scanner</span>
              </button>
            )}
          </div>

          {/* Status Alert Banner */}
          <div className={`p-4 rounded-xl border text-xs font-bold transition-all ${
            statusType === 'success' ? 'bg-emerald-950/80 border-emerald-500/40 text-emerald-300' :
            statusType === 'active' ? 'bg-blue-950/80 border-blue-500/40 text-blue-300' :
            statusType === 'error' ? 'bg-rose-950/80 border-rose-500/40 text-rose-300' :
            'bg-[#141724] border-[#232740] text-slate-400'
          }`}>
            <div className="flex items-center gap-2">
              {statusType === 'success' ? <CheckCircle2 className="w-4 h-4 text-emerald-400" /> : <AlertCircle className="w-4 h-4" />}
              <span>{statusMessage}</span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
