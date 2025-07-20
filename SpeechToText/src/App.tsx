import { createAndUpdateOrder } from "./api/orderAPI";


import React, {
    useState,
    useRef,
    useEffect,
    useCallback,
    memo,
    Fragment,
    ChangeEvent,
} from "react";
import {
    ThemeProvider,
    createTheme,
    CssBaseline,
    Container,
    Card,
    CardContent,
    CardHeader,
    Typography,
    Button,
    TextField,
    Stack,
    IconButton,
    FormControl,
    InputLabel,
    MenuItem,
    Select,
    SelectChangeEvent,
    Grid,
    Box,
} from "@mui/material";
import {
    Mic,
    MicOff,
    CopyAll,
    Check,
    LightMode,
    DarkMode,
    Clear,
    Download,
} from "@mui/icons-material";


/* ------------------------------------------------------------------
   TYPE DECLARATIONS FOR SPEECH RECOGNITION
------------------------------------------------------------------- */
const recognition = window.SpeechRecognition || window.webkitSpeechRecognition;
if (recognition) {
    const recognitionInstance = new recognition();
   
    recognitionInstance.start();
}


/* ------------------------------------------------------------------
   THEMES
------------------------------------------------------------------- */
const lightTheme = createTheme({
    palette: {
        mode: "light",
        primary: {
            main: "#2563eb",
        },
        error: {
            main: "#ef4444",
        },
        background: {
            default: "#f3f4f6",
        },
    },
    typography: {
        fontFamily: "'Poppins', sans-serif",
        fontSize: 16,
        h4: {
            fontSize: "2rem",
            fontWeight: 700,
        },
        body1: {
            fontSize: "1.125rem",
        },
        button: {
            textTransform: "none",
            fontSize: "1.125rem",
        },
    },
});


const darkTheme = createTheme({
    palette: {
        mode: "dark",
        primary: {
            main: "#3b82f6",
        },
        error: {
            main: "#f87171",
        },
        background: {
            default: "#1e293b",
            paper: "#2d3748",
        },
    },
    typography: {
        fontFamily: "'Poppins', sans-serif",
        fontSize: 16,
        h4: {
            fontSize: "2rem",
            fontWeight: 700,
        },
        body1: {
            fontSize: "1.125rem",
        },
        button: {
            textTransform: "none",
            fontSize: "1.125rem",
        },
    },
});


/* ------------------------------------------------------------------
   HEADER COMPONENT
------------------------------------------------------------------- */


interface AppHeaderProps {
    darkMode: boolean;
    onToggleDarkMode: () => void;
    answer?: string; // New prop for the answer
}


const AppHeader = memo(function AppHeader({
    darkMode,
    onToggleDarkMode,
    answer
}: AppHeaderProps) {


/*
    useEffect(() => {
        if (answer && 'speechSynthesis' in window) {
            // Cancel any ongoing speech
            window.speechSynthesis.cancel();
           
            // Create and speak new utterance
            const utterance = new SpeechSynthesisUtterance(answer);
            window.speechSynthesis.speak(utterance);
        }
    }, [answer]);  // Trigger the effect when 'answer' changes
*/
    return (
        <CardHeader
            title={
                <Box>
                    <Typography variant="h4" fontWeight="bold">
                        Welcome to Mapit.ai, please place your order!
                    </Typography>
                    {answer && (
                        <Typography
                            variant="body1"
                            sx={{
                                mt: 1,
                                color: 'text.secondary',
                                fontStyle: 'italic'
                            }}
                        >
                            {answer}
                        </Typography>
                    )}
                </Box>
            }
            action={
                <IconButton onClick={onToggleDarkMode} title="Toggle Theme">
                    {darkMode ? <LightMode /> : <DarkMode />}
                </IconButton>
            }
        />
    );
});


/* ------------------------------------------------------------------
   LANGUAGE SELECTOR COMPONENT
------------------------------------------------------------------- */
interface LanguageSelectorProps {
    language: string;
    onChangeLanguage: (newLanguage: string) => void;
}


const LanguageSelector = memo(function LanguageSelector({
    language,
    onChangeLanguage,
}: LanguageSelectorProps) {
    const handleSelectChange = (e: SelectChangeEvent) => {
        onChangeLanguage(e.target.value as string);
    };


    return (
        <FormControl fullWidth>
            <InputLabel id="language-select-label">Language</InputLabel>
            <Select
                labelId="language-select-label"
                value={language}
                label="Language"
                onChange={handleSelectChange}
                sx={{ borderRadius: 2 }}
            >
                <MenuItem value="en-US">English (US)</MenuItem>
                <MenuItem value="en-GB">English (UK)</MenuItem>
                <MenuItem value="es-ES">Spanish (ES)</MenuItem>
                <MenuItem value="fr-FR">French (FR)</MenuItem>
                <MenuItem value="de-DE">German (DE)</MenuItem>
                <MenuItem value="ar-IN">Arabic (IN)</MenuItem>
            </Select>
        </FormControl>
    );
});


/* ------------------------------------------------------------------
   CONTROL BUTTONS COMPONENT
------------------------------------------------------------------- */
interface ControlButtonsProps {
    isListening: boolean;
    text: string;
    interimText: string;
    copied: boolean;
    onStart: () => void;
    onStop: () => void;
    onCopy: () => void;
    onClear: () => void;
    onExport: () => void;
}


const ControlButtons = memo(function ControlButtons({
    isListening,
    text,
    interimText,
    copied,
    onStart,
    onStop,
    onCopy,
    onClear,
    onExport,
}: ControlButtonsProps) {
    return (
        <Stack direction={{ xs: "column", sm: "row" }} spacing={2}>
            <Button
                variant="contained"
                color="primary"
                onClick={onStart}
                disabled={isListening}
                sx={{
                    fontWeight: "bold",
                    borderRadius: 2,
                }}
                fullWidth
            >
                <Mic sx={{ mr: 1 }} /> Start
            </Button>


            <Button
                variant="contained"
                color="error"
                onClick={onStop}
                disabled={!isListening}
                sx={{
                    fontWeight: "bold",
                    borderRadius: 2,
                }}
                fullWidth
            >
                <MicOff sx={{ mr: 1 }} /> Stop
            </Button>
{/*
            <Button
                variant="outlined"
                color="secondary"
                onClick={onCopy}
                disabled={!text && !interimText}
                sx={{
                    borderRadius: 2,
                    fontWeight: "bold",
                }}
                fullWidth
            >
                {copied ? (
                    <Fragment>
                        <Check sx={{ mr: 1 }} /> Copied!
                    </Fragment>
                ) : (
                    <Fragment>
                        <CopyAll sx={{ mr: 1 }} /> Copy
                    </Fragment>
                )}
            </Button>


            <Button
                variant="outlined"
                color="inherit"
                onClick={onClear}
                disabled={!text && !interimText}
                sx={{
                    borderRadius: 2,
                    fontWeight: "bold",
                }}
                fullWidth
            >
                <Clear sx={{ mr: 1 }} /> Clear
            </Button>


            <Button
                variant="outlined"
                color="success"
                onClick={onExport}
                disabled={!text && !interimText}
                sx={{
                    borderRadius: 2,
                    fontWeight: "bold",
                }}
                fullWidth
            >
                <Download sx={{ mr: 1 }} /> Export
            </Button>
            */}
        </Stack>
    );
});


/* ------------------------------------------------------------------
   TEXT AREA COMPONENT
------------------------------------------------------------------- */


interface OrderDetails {
    order_details?: string;
    sizes?: string;
    toppings?: string;
    answer?: string;
}




interface TranscribedTextAreaProps {
    text: string;
    interimText: string;
    onChange: (value: string) => void;
}


const TranscribedTextArea = memo(function TranscribedTextArea({
    text,
    interimText,
    onChange,
}: TranscribedTextAreaProps) {
    const handleTextChange = (e: ChangeEvent<HTMLInputElement>) => {
        onChange(e.target.value);
    };


    return (
        <TextField
            label="Transcribed Text"
            multiline
            minRows={12}
            value={text + interimText}
            onChange={handleTextChange}
            placeholder="Your speech will appear here..."
            fullWidth
            InputProps={{
                readOnly: true,
            }}
            sx={{
                borderRadius: 2,
                backgroundColor: "background.default",
                fontSize: "1.25rem",
            }}
        />
    );
});


/* ------------------------------------------------------------------
   MAIN COMPONENT
------------------------------------------------------------------- */
const App: React.FC = () => {
    const [isListening, setIsListening] = useState<boolean>(false);
    const [text, setText] = useState<string>("");
    const [interimText, setInterimText] = useState<string>("");
    const [error, setError] = useState<string>("");
    const [copied, setCopied] = useState<boolean>(false);
    const [darkMode, setDarkMode] = useState<boolean>(false);
    const [language, setLanguage] = useState<string>("en-US");
    const [data, setData] = useState({});
    const recognitionRef = useRef<SpeechRecognition | null>(null);
    const lastSentTextRef = useRef<string>("");
    const [isProcessing, setIsProcessing] = useState<boolean>(false);
    const pendingTextRef = useRef<string>("");
    const processingTimeoutRef = useRef<number | null>(null);


    const getText = async (text: string) => {
        try {
            setIsProcessing(true);
            const responseData = await createAndUpdateOrder(text);
            setData({ ...responseData });
        } catch (error) {
            console.error("Failed to fetch order data:", error);
            setError("Failed to process the order. Please try again.");
        } finally {
            setIsProcessing(false);
           
            // Process any pending text after current request is done
            if (pendingTextRef.current) {
                const textToProcess = pendingTextRef.current;
                pendingTextRef.current = "";
                getText(textToProcess);
            }
        }
    };


    useEffect(() => {
        const newText = text.slice(lastSentTextRef.current.length);
        if (!newText) return;


        // Clear any existing timeout
        if (processingTimeoutRef.current) {
            window.clearTimeout(processingTimeoutRef.current);
        }


        // Set a new timeout to handle the text
        processingTimeoutRef.current = window.setTimeout(() => {
            if (isProcessing) {
                // If currently processing, store this text as pending
                pendingTextRef.current = newText;
            } else {
                // If not processing, send the request
                getText(newText);
            }
            lastSentTextRef.current = text;
        }, 1000); // Wait 1 second after last speech recognition update


        // Cleanup timeout on unmount
        return () => {
            if (processingTimeoutRef.current) {
                window.clearTimeout(processingTimeoutRef.current);
            }
        };
    }, [text, isProcessing]);


    const initializeRecognition = useCallback(() => {
        if (!recognitionRef.current) {
            const SpeechRecognition =
                window.SpeechRecognition || window.webkitSpeechRecognition;


            if (!SpeechRecognition) {
                setError("Your browser does not support Speech Recognition.");
                return;
            }


            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = true;
            recognition.lang = language;


            recognition.onstart = () => {
                setIsListening(true);
                setError("");
            };


            recognition.onerror = (event: SpeechRecognitionErrorEvent) => {
                setError(
                    `Error occurred: ${event.error}. Please check your microphone permissions.`
                );
            };


            recognition.onend = () => {
                setIsListening(false);
            };


            recognition.onresult = (event: SpeechRecognitionEvent) => {
                let finalTranscript = "";
                let interimTranscript = "";


                for (let i = event.resultIndex; i < event.results.length; i++) {
                    if (event.results[i].isFinal) {
                        finalTranscript += event.results[i][0].transcript;
                    } else {
                        interimTranscript += event.results[i][0].transcript;
                    }
                }


                setText((prev) => prev + finalTranscript);
                setInterimText(interimTranscript);
            };


            recognitionRef.current = recognition;
        }
    }, [language]);


    const startListening = useCallback(() => {
        initializeRecognition();
        if (recognitionRef.current) {
            recognitionRef.current.start();
        }
    }, [initializeRecognition]);


    const stopListening = useCallback(() => {
        if (recognitionRef.current) {
            recognitionRef.current.stop();
        }
        setIsListening(false);
        setInterimText("");
    }, []);


    const handleCopy = useCallback(() => {
        const fullText = text + interimText;
        navigator.clipboard.writeText(fullText).then(() => {
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        });
    }, [text, interimText]);


    const handleClear = useCallback(() => {
        setText("");
        setInterimText("");
        setError("");
    }, []);


    const handleExport = useCallback(() => {
        const blob = new Blob([text + interimText], {
            type: "text/plain;charset=utf-8",
        });
        const url = URL.createObjectURL(blob);
        const link = document.createElement("a");
        link.href = url;
        link.download = "transcript.txt";
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
        URL.revokeObjectURL(url);
    }, [text, interimText]);


    useEffect(() => {
        return () => {
            if (recognitionRef.current) {
                recognitionRef.current.stop();
            }
        };
    }, []);


   
    return (
        <ThemeProvider theme={darkMode ? darkTheme : lightTheme}>
            <CssBaseline />
            <Container
                maxWidth="xl"
                sx={{
                    minHeight: "100vh",
                    display: "flex",
                    alignItems: "center",
                    justifyContent: "center",
                    p: 2,
                }}
            >
                <Grid container spacing={3}>
                    {/* Main Content Area */}
                    <Grid item xs={12} md={8}>
                        <Card
                            sx={{
                                width: "100%",
                                boxShadow: 6,
                                borderRadius: 3,
                                p: 3,
                                backgroundColor: "background.paper",
                            }}
                        >
                            <AppHeader
                            darkMode={darkMode}
                            onToggleDarkMode={() => setDarkMode((prev) => !prev)}
                            answer={(data as OrderDetails).answer}
                            />


                            <CardContent>
                                <Stack spacing={4}>
                                    <LanguageSelector
                                        language={language}
                                        onChangeLanguage={setLanguage}
                                    />


                                    <ControlButtons
                                        isListening={isListening}
                                        text={text}
                                        interimText={interimText}
                                        copied={copied}
                                        onStart={startListening}
                                        onStop={stopListening}
                                        onCopy={handleCopy}
                                        onClear={handleClear}
                                        onExport={handleExport}
                                    />


                                    <TranscribedTextArea
                                        text={text}
                                        interimText={interimText}
                                        onChange={(val) => setText(val)}
                                    />


                                    {error && (
                                        <Typography
                                            color="error"
                                            variant="body2"
                                        >
                                            {error}
                                        </Typography>
                                    )}
                                </Stack>
                            </CardContent>
                        </Card>
                    </Grid>


                    {/* Order Panel */}
                    <Grid item xs={12} md={4}>
                        <Card
                            sx={{
                                width: "100%",
                                height: "100%",
                                boxShadow: 6,
                                borderRadius: 3,
                                backgroundColor: "background.paper",
                            }}
                        >
                            <CardHeader
                                title={
                                    <Typography variant="h5" fontWeight="bold">
                                        Order Details
                                    </Typography>
                                }
                            />
                            <CardContent>
                                <Box
                                    sx={{
                                        p: 2,
                                        bgcolor: "background.default",
                                        borderRadius: 2,
                                        minHeight: "400px",
                                        maxHeight: "600px",
                                        overflowY: "auto",
                                    }}
                                >
                                    {data && typeof data === "object" && (
                                        <Stack spacing={3}>
                                            {(() => {
                                                const items =
                                                    (
                                                        data as OrderDetails
                                                    ).order_details?.split(
                                                        ","
                                                    ) || [];
                                                const sizes =
                                                    (
                                                        data as OrderDetails
                                                    ).sizes?.split(",") || [];
                                                const toppings =
                                                    (
                                                        data as OrderDetails
                                                    ).toppings?.split(",") ||
                                                    [];


                                                return items.map(
                                                    (
                                                        item: string,
                                                        index: number
                                                    ) => (
                                                        <Box key={index}>
                                                            <Typography
                                                                variant="body1"
                                                                sx={{
                                                                    fontFamily:
                                                                        "'Roboto Mono', monospace",
                                                                    fontWeight: 500,
                                                                    fontSize:
                                                                        "1.1rem",
                                                                }}
                                                            >
                                                                {item.trim()}
                                                            </Typography>
                                                            <Box
                                                                sx={{
                                                                    display:
                                                                        "flex",
                                                                    alignItems:
                                                                        "center",
                                                                    gap: 1,
                                                                    mt: 0.5,
                                                                }}
                                                            >
                                                                {sizes[
                                                                    index
                                                                ] && (
                                                                    <Typography
                                                                        variant="body2"
                                                                        sx={{
                                                                            fontFamily:
                                                                                "'Roboto Mono', monospace",
                                                                            color: "text.secondary",
                                                                            fontSize:
                                                                                "0.9rem",
                                                                            fontStyle:
                                                                                "italic",
                                                                        }}
                                                                    >
                                                                        Size:{" "}
                                                                        {sizes[
                                                                            index
                                                                        ]
                                                                            .trim()
                                                                            .split(
                                                                                "x"
                                                                            )[1]
                                                                            .trim()}
                                                                    </Typography>
                                                                )}
                                                                {toppings[
                                                                    index
                                                                ] && (
                                                                    <Typography
                                                                        variant="body2"
                                                                        sx={{
                                                                            fontFamily:
                                                                                "'Roboto Mono', monospace",
                                                                            color: "text.secondary",
                                                                            fontSize:
                                                                                "0.9rem",
                                                                            "&::before":
                                                                                {
                                                                                    content:
                                                                                        '"|"',
                                                                                    marginRight:
                                                                                        "4px",
                                                                                },
                                                                        }}
                                                                    >
                                                                        Toppings:{" "}
                                                                        {toppings[
                                                                            index
                                                                        ]
                                                                            .trim()
                                                                            .split(
                                                                                "x"
                                                                            )[1]
                                                                            .trim()}
                                                                    </Typography>
                                                                )}
                                                            </Box>
                                                        </Box>
                                                    )
                                                );
                                            })()}
                                        </Stack>
                                    )}
                                </Box>
                            </CardContent>
                        </Card>
                    </Grid>
                </Grid>
            </Container>
        </ThemeProvider>
    );
};


export default App;
