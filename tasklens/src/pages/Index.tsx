import { useState, useRef, useEffect } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2, Camera, ScanLine, RefreshCw, Mic, MicOff, CheckCircle2, Circle } from "lucide-react";
import { toast } from "sonner";

type AppState = "setup" | "capture" | "analysis";

const Index = () => {
  const [appState, setAppState] = useState<AppState>("setup");
  const [goal, setGoal] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [capturedImage, setCapturedImage] = useState<string>("");
  const [currentStep, setCurrentStep] = useState(1);
  const [isRecording, setIsRecording] = useState(false);
  
  const videoRef = useRef<HTMLVideoElement>(null);
  const hiddenCanvasRef = useRef<HTMLCanvasElement>(null);
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const recognitionRef = useRef<any>(null);

  useEffect(() => {
    // Initialize speech recognition
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition;
    if (SpeechRecognition) {
      recognitionRef.current = new SpeechRecognition();
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';

      recognitionRef.current.onresult = (event: any) => {
        const transcript = event.results[0][0].transcript;
        setGoal(transcript);
        toast.success("Voice input captured");
      };

      recognitionRef.current.onerror = (event: any) => {
        console.error("Speech recognition error:", event.error);
        toast.error("Voice input failed. Please try again.");
        setIsRecording(false);
      };

      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
    }

    return () => {
      // Cleanup: stop video stream when component unmounts
      if (streamRef.current) {
        streamRef.current.getTracks().forEach(track => track.stop());
      }
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const startCamera = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ 
        video: { facingMode: "environment" },
        audio: false 
      });
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        streamRef.current = stream;
        setAppState("capture");
        toast.success("Camera activated");
      }
    } catch (error) {
      console.error("Camera access error:", error);
      toast.error("Unable to access camera. Please check permissions.");
    }
  };

  const captureFrame = () => {
    if (!videoRef.current || !hiddenCanvasRef.current) return;
    
    setIsLoading(true);
    
    const video = videoRef.current;
    const canvas = hiddenCanvasRef.current;
    const context = canvas.getContext("2d");
    
    if (context) {
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;
      context.drawImage(video, 0, 0, canvas.width, canvas.height);
      
      const imageData = canvas.toDataURL("image/png");
      setCapturedImage(imageData);
      
      // Simulate processing delay
      setTimeout(() => {
        setIsLoading(false);
        setAppState("analysis");
        
        // If this is a verification scan (not the first capture)
        if (capturedImage) {
          verifyAndContinue();
        } else {
          toast.success("Frame captured and analyzed");
        }
      }, 1500);
    }
  };

  const rescan = () => {
    setCapturedImage("");
    setCurrentStep(1);
    setAppState("capture");
  };

  const continueToNextStep = () => {
    setAppState("capture");
    toast.info(`Position your hardware and scan to verify Step ${currentStep}`);
  };

  const verifyAndContinue = () => {
    setCurrentStep(prev => prev + 1);
    toast.success(`Step ${currentStep} verified! Moving to step ${currentStep + 1}`);
  };

  const toggleVoiceInput = () => {
    if (!recognitionRef.current) {
      toast.error("Voice input not supported in this browser");
      return;
    }

    if (isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    } else {
      setIsRecording(true);
      recognitionRef.current.start();
      toast.info("Listening...");
    }
  };

  return (
    <div className="min-h-screen bg-background text-foreground flex flex-col relative overflow-hidden">
      {/* Setup Screen */}
      <div 
        className={`absolute inset-0 flex flex-col items-center justify-center p-6 transition-all duration-500 ${
          appState === "setup" ? "opacity-100 scale-100" : "opacity-0 scale-95 pointer-events-none"
        }`}
      >
        <div className="text-center space-y-8 max-w-md">
          <div className="space-y-4">
            <div className="w-20 h-20 mx-auto rounded-full bg-primary/20 flex items-center justify-center animate-pulse-glow">
              <Camera className="w-10 h-10 text-primary" />
            </div>
            <h1 className="text-5xl font-bold tracking-tight">
              Task<span className="text-primary">Lens</span>
            </h1>
            <p className="text-xl text-muted-foreground">AI Hardware Architect</p>
          </div>
          
          <p className="text-muted-foreground leading-relaxed">
            Point your camera at hardware components and receive real-time, step-by-step guidance for assembly and troubleshooting.
          </p>
          
          <Button 
            id="start-feed-btn"
            onClick={startCamera}
            size="lg"
            className="w-full h-14 text-lg font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all hover:shadow-[0_0_30px_hsl(var(--primary)/0.5)]"
          >
            <Camera className="mr-2 h-5 w-5" />
            Start Live Camera Feed
          </Button>
        </div>
      </div>

      {/* Capture Screen */}
      <div 
        className={`absolute inset-0 flex flex-col transition-all duration-500 ${
          appState === "capture" ? "opacity-100 scale-100" : "opacity-0 scale-95 pointer-events-none"
        }`}
      >
        <Tabs defaultValue="video" className="flex-1 flex flex-col">
          <div className="bg-background/95 backdrop-blur-sm border-b border-primary/20">
            <TabsList className="w-full h-14 bg-transparent rounded-none grid grid-cols-2">
              <TabsTrigger 
                value="video" 
                className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary"
              >
                <Camera className="mr-2 h-4 w-4" />
                Live Feed
              </TabsTrigger>
              <TabsTrigger 
                value="tasks"
                className="data-[state=active]:bg-primary/20 data-[state=active]:text-primary"
              >
                <CheckCircle2 className="mr-2 h-4 w-4" />
                Task List
              </TabsTrigger>
            </TabsList>
          </div>

          <TabsContent value="video" className="flex-1 relative m-0">
            <video
              id="live-video"
              ref={videoRef}
              autoPlay
              playsInline
              muted
              className="w-full h-full object-cover"
            />
            
            <div className="absolute bottom-0 left-0 right-0 p-6 bg-gradient-to-t from-black/80 via-black/50 to-transparent">
              <div className="space-y-4 max-w-lg mx-auto">
                <div className="flex items-center gap-2 bg-background/50 backdrop-blur-sm rounded-lg p-3 border border-primary/30">
                  <label className="text-sm font-medium text-primary whitespace-nowrap">Goal:</label>
                  <Input
                    id="goal-input"
                    value={goal}
                    onChange={(e) => setGoal(e.target.value)}
                    placeholder="e.g., Blink an LED"
                    className="border-0 bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0"
                  />
                  <Button
                    onClick={toggleVoiceInput}
                    variant="ghost"
                    size="icon"
                    className={`flex-shrink-0 ${isRecording ? 'text-destructive animate-pulse' : 'text-primary'}`}
                    title={isRecording ? "Stop recording" : "Start voice input"}
                  >
                    {isRecording ? <MicOff className="h-5 w-5" /> : <Mic className="h-5 w-5" />}
                  </Button>
                </div>
                
                <Button
                  id="scan-btn"
                  onClick={captureFrame}
                  disabled={!goal.trim()}
                  size="lg"
                  className="w-full h-14 text-lg font-semibold bg-primary text-primary-foreground hover:bg-primary/90 transition-all hover:shadow-[0_0_30px_hsl(var(--primary)/0.5)]"
                >
                  <ScanLine className="mr-2 h-5 w-5" />
                  Scan & Analyze Frame
                </Button>
              </div>
            </div>
          </TabsContent>

          <TabsContent value="tasks" className="flex-1 overflow-y-auto m-0 p-6 bg-background">
            <div className="max-w-2xl mx-auto space-y-6">
              <div className="space-y-2">
                <h2 className="text-2xl font-bold text-primary">Task Checklist</h2>
                <p className="text-muted-foreground">Complete these steps to achieve your goal</p>
              </div>

              <div className="space-y-3">
                {[
                  { id: 1, title: "Identify Components", description: "Locate Arduino board, LED, resistor, and jumper wires", completed: false },
                  { id: 2, title: "Connect Power", description: "Connect Arduino to power source via USB cable", completed: false },
                  { id: 3, title: "Wire LED Circuit", description: "Connect LED positive leg to GPIO pin 17 through 220Ω resistor", completed: false },
                  { id: 4, title: "Connect Ground", description: "Connect LED negative leg to GND pin on board", completed: false },
                  { id: 5, title: "Upload Code", description: "Load the blink sketch to your Arduino board", completed: false },
                  { id: 6, title: "Verify & Test", description: "Confirm LED blinks at expected interval", completed: false },
                ].map((task) => (
                  <div
                    key={task.id}
                    className="bg-card border border-primary/20 rounded-lg p-4 hover:border-primary/40 transition-colors"
                  >
                    <div className="flex items-start gap-3">
                      <div className="mt-1">
                        {task.completed ? (
                          <CheckCircle2 className="h-5 w-5 text-primary" />
                        ) : (
                          <Circle className="h-5 w-5 text-muted-foreground" />
                        )}
                      </div>
                      <div className="flex-1 space-y-1">
                        <h3 className="font-semibold text-foreground">
                          Step {task.id}: {task.title}
                        </h3>
                        <p className="text-sm text-muted-foreground">{task.description}</p>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              <div className="bg-primary/10 border border-primary/30 rounded-lg p-4">
                <p className="text-sm text-foreground">
                  💡 <strong>Tip:</strong> Switch to the Live Feed tab to scan your hardware and get real-time guidance for each step.
                </p>
              </div>
            </div>
          </TabsContent>
        </Tabs>
      </div>

      {/* Analysis Screen */}
      <div 
        className={`absolute inset-0 flex flex-col transition-all duration-500 ${
          appState === "analysis" ? "opacity-100 scale-100" : "opacity-0 scale-95 pointer-events-none"
        }`}
      >
        <div className="flex-1 overflow-y-auto">
          {/* Visual Area */}
          <div id="visual-area" className="relative">
            <img
              id="captured-photo"
              src={capturedImage}
              alt="Captured frame"
              className="w-full h-auto"
            />
            <canvas
              id="port-canvas"
              ref={overlayCanvasRef}
              className="absolute top-0 left-0 w-full h-full pointer-events-none"
            />
          </div>

          {/* Instruction Panel */}
          <div className="p-6 space-y-6 bg-card border-t border-border">
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-primary">Assembly Guide</h2>
                <span className="text-sm text-muted-foreground">Goal: {goal}</span>
              </div>

              <Select disabled={isLoading}>
                <SelectTrigger id="chronology-dropdown" className="w-full">
                  <SelectValue placeholder="Step-by-step chronology" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="step1">Step 1: Identify Components</SelectItem>
                  <SelectItem value="step2">Step 2: Connect Power</SelectItem>
                  <SelectItem value="step3">Step 3: Wire LED Circuit</SelectItem>
                  <SelectItem value="step4">Step 4: Program & Test</SelectItem>
                </SelectContent>
              </Select>

              <div 
                id="instruction-text"
                className="bg-secondary/50 rounded-lg p-4 space-y-3 border border-primary/20"
              >
                <div className="flex items-start gap-3">
                  <div className="w-8 h-8 rounded-full bg-primary/20 flex items-center justify-center flex-shrink-0 mt-1">
                    <span className="text-primary font-bold">{currentStep}</span>
                  </div>
                  <div className="space-y-2">
                    <h3 className="font-semibold text-lg">Connect LED to GPIO Pin</h3>
                    <p className="text-muted-foreground leading-relaxed">
                      Connect the LED's positive leg (longer leg) to GPIO pin 17 through a 220Ω resistor. 
                      Connect the negative leg (shorter leg) to the GND pin on your board.
                    </p>
                    <div className="bg-destructive/10 border border-destructive/30 rounded p-3 mt-3">
                      <p className="text-sm text-destructive-foreground">
                        ⚠️ <strong>Safety:</strong> Always disconnect power before wiring. 
                        Verify polarity before connecting.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="flex gap-3">
              <Button
                id="continue-btn"
                onClick={continueToNextStep}
                className="flex-1 h-12 bg-primary text-primary-foreground hover:bg-primary/90"
              >
                <Camera className="mr-2 h-4 w-4" />
                Take Verification Photo
              </Button>
              <Button
                id="rescan-btn"
                onClick={rescan}
                variant="outline"
                className="h-12 px-6"
              >
                <RefreshCw className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      {/* Loading Spinner Overlay */}
      {isLoading && (
        <div 
          id="loading-spinner"
          className="absolute inset-0 bg-background/95 backdrop-blur-sm flex items-center justify-center z-50 animate-fade-in"
        >
          <div className="text-center space-y-4">
            <Loader2 className="w-16 h-16 text-primary animate-spin mx-auto" />
            <p className="text-lg text-muted-foreground">Analyzing frame...</p>
          </div>
        </div>
      )}

      {/* Hidden Canvas for Frame Capture */}
      <canvas ref={hiddenCanvasRef} id="hidden-canvas" className="hidden" />
    </div>
  );
};

export default Index;
