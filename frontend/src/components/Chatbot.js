import React, { useState, useRef, useEffect } from "react";
import { useAuth } from "../context/AuthContext";
import axios from "axios";
import {
  MainContainer,
  ChatContainer,
  MessageList,
  Message,
  TypingIndicator,
  MessageInput,
  SendButton,
} from "@chatscope/chat-ui-kit-react";
import toast from "react-hot-toast";
import styles from "@chatscope/chat-ui-kit-styles/dist/default/styles.min.css";
import { SendHorizontal } from "lucide-react";

const Chatbot = () => {
  const [auth] = useAuth();
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [webUrl, setWebUrl] = useState("");
  const [selectedFile, setSelectedFile] = useState(null);
  const [isListening, setIsListening] = useState(false);
  const [typing, setTyping] = useState(false);
  const [isAudioPlaying, setIsAudioPlaying] = useState(false);
  const [loading, setLoading] = useState({
    webUrl: false,
    youtubeUrl: false,
    pdfUrl: false,
  });

  const [firstAnswerGenerated, setFirstAnswerGenerated] = useState(false);
  const [messages, setMessages] = useState("");

  const handleFileUpload = async (e) => {
    e.preventDefault();
    try {
      setLoading({ ...loading, pdfUrl: true });
      const formData = new FormData();
      formData.append("file", selectedFile);
      formData.append("id", auth?.user?.id);

      const response = await axios.post(
        `${process.env.REACT_APP_API}/api/processpdf`,
        formData,
        {
          headers: {
            "Content-Type": "multipart/form-data",
            Authorization: `Bearer ${auth?.token}`,
          },
        }
      );
      if (response.data.success === true) {
        toast.success("Processing Successfull");
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      toast.error("Error Processing");
    } finally {
      setLoading({ ...loading, pdfUrl: false });
    }
  };

  const handleYoutubeUrl = async (e) => {
    e.preventDefault();
    try {
      setLoading({ ...loading, youtubeUrl: true });
      const response = await axios.post(
        `${process.env.REACT_APP_API}/api/processvideo`,
        {
          video_url: youtubeUrl,
          id: auth?.user?.id,
        },
        { headers: { Authorization: `Bearer ${auth?.token}` } }
      );
      if (response.data.success === true) {
        toast.success("processing successfull");
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      toast.error("Error Processing");
    } finally {
      setLoading({
        ...loading,
        youtubeUrl: false,
      });
    }
  };

  const handleWebUrl = async (e) => {
    e.preventDefault();
    try {
      setLoading({ ...loading, webUrl: true });
      const response = await axios.post(
        `${process.env.REACT_APP_API}/api/process-url`,
        {
          url: webUrl,
          id: auth?.user?.id,
        },
        { headers: { Authorization: `Bearer ${auth?.token}` } }
      );
      if (response.data.success === true) {
        toast.success("processing successfull");
      } else {
        toast.error(response.data.message);
      }
    } catch (error) {
      toast.error("Error Processing");
    } finally {
      setLoading({ ...loading, webUrl: false });
    }
  };

  // .....................................................................
  const currentAudio = useRef(new Audio());
  
  const handleSpeechRecognition = () => {
    const recognition = new window.webkitSpeechRecognition();
    recognition.onstart = () => {
      setIsListening(true);
    };
    recognition.onresult = async (event) => {
      if (event.results && event.results[0]) {
        const speechResult = event.results[0][0].transcript;
        setMessages(speechResult);
      } else {
        toast.error("Something Went Wrong");
      }
    };
    recognition.start();
    recognition.onend = () => {
      setIsListening(false);
    };
  };

  const userKey = "NILZaBiKktP3P6fiFgIIdDTV5AC3";
  const secretKey = "be4b0c3fa42549fcad661b7c7406f84c";
  
  const convertTextToSpeech = async (generatedText) => {
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API}/api/tts`,
        {
          text: generatedText,
        },
        { headers: { Authorization: `Bearer ${auth?.token}` } }
      );

      if (response.data.audioUrl) {
        let audioUrl = response.data.audioUrl;
        if (!currentAudio.current.paused) {
          currentAudio.current.pause();
        }
        currentAudio.current = new Audio(audioUrl);
        currentAudio.current.play();
        setIsAudioPlaying(true);
        currentAudio.current.onended = () => {
          setIsAudioPlaying(false);
        };
      } else {
        throw new Error("Failed to fetch audio");
      }
    } catch (error) {
      console.error("Error converting text to speech:", error);
    }
  };

  const handlePlayGeneratedText = (generatedText) => {
    convertTextToSpeech(generatedText);
    setFirstAnswerGenerated(true);
  };

  const toggleAudioPlayback = () => {
    try {
      if (currentAudio.current) {
        if (currentAudio.current.paused) {
          currentAudio.current
            .play()
            .catch((error) => console.error("Audio playback error:", error));
        } else {
          currentAudio.current.pause();
        }
        setIsAudioPlaying(!currentAudio.current.paused);
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };
  const callGPTAPI = async (inputText) => {
    try {
      const response = await axios.post(
        `${process.env.REACT_APP_API}/api/ask`,
        {
          question: inputText,
          id: auth?.user?.id,
        },
        { headers: { Authorization: `Bearer ${auth?.token}` } }
      );
      return response.data.responses[0];
    } catch (error) {
      toast.error("Something Went Wrong");
    }
  };

// .....................................................................



  const [inputInitHeight, setInputInitHeight] = useState(0);

  useEffect(() => {
    const chatInput = document.querySelector('.chat-input textarea');
    setInputInitHeight(chatInput.scrollHeight);
  }, []);

  const createChatLi = (message, className) => {
    const chatLi = document.createElement('li');
    chatLi.classList.add('chat', className);
    let chatContent = className === 'outgoing' ? `<p></p>` : `<p></p>`;
    chatLi.innerHTML = chatContent;
    chatLi.querySelector('p').textContent = message;
    return chatLi;
  };

  const generateResponse = (chatElement) => {
    
    const API_URL = `${process.env.REACT_APP_API}/api/ask`;
    const messageElement = chatElement.querySelector('p');

    const requestOptions = {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Authorization: `Bearer ${auth.token}`,
      },
      body: JSON.stringify({
        question: messages,
      }),
    };

    fetch(API_URL, requestOptions)
      .then((res) => res.json())
      .then((data) => {
        if (data.success === true){
          messageElement.textContent = data.response
          handlePlayGeneratedText(data.response)
        }
        else{
          messageElement.classList.add('error');
          if(!data.error){
            messageElement.textContent = data.message;
            handlePlayGeneratedText(data.message)
          } else {
            messageElement.textContent = data.error;
            handlePlayGeneratedText(data.error)
          }
        }
      })
      .finally(() => {
        const chatbox = document.querySelector('.chatbox');
        chatbox.scrollTo(0, chatbox.scrollHeight);
      });
  };

  const handleChat = () => {
    if (!currentAudio.current.paused) {
      currentAudio.current.pause();
    }
    const chatInput = document.querySelector('.chat-input textarea');
    const chatbox = document.querySelector('.chatbox');

    const trimmedMessage = messages.trim();
    if (!trimmedMessage) return;

    setMessages('');
    chatInput.style.height = `${inputInitHeight}px`;

    const outgoingChatLi = createChatLi(trimmedMessage, 'outgoing');
    chatbox.appendChild(outgoingChatLi);
    chatbox.scrollTo(0, chatbox.scrollHeight);

    setTimeout(() => {
      const incomingChatLi = createChatLi('Thinking...', 'incoming');
      chatbox.appendChild(incomingChatLi);
      chatbox.scrollTo(0, chatbox.scrollHeight);
      generateResponse(incomingChatLi);
    }, 600);
  };

  const handleInputChange = (e) => {
    setMessages(e.target.value)
    const chatInput = document.querySelector('.chat-input textarea');
    chatInput.style.height = `${inputInitHeight}px`;
    chatInput.style.height = `${chatInput.scrollHeight}px`;
  };

  const handleInputKeyDown = (e) => {
    const chatInput = document.querySelector('.chat-input textarea');
    if (e.key === 'Enter' && !e.shiftKey && window.innerWidth > 800) {
      e.preventDefault();
      handleChat();
    }
  };
   

  return (
    <>
      <section className="m-0 p-0">
        <div className="container-fluid ">
          <div className="row justify-content-center align-items-center h-100">
            <div className="col-md-5 col-lg-4 text-center">
              <img
                className="w-25 mb-2 mt-4 mx-auto d-none d-md-block"
                src="/MinerImg.png"
                alt="Logo 3"
              />
              <div className="animate seven d-none d-md-block">
                <span className="black">T</span>
                <span className="black">E</span>
                <span className="black">X</span>
                <span className="yellow">M</span>
                <span className="yellow">I</span>
                <span className="yellow">N </span>
                <span className="black">G</span>
                <span className="black">P</span>
                <span className="black">T</span>
              </div>
              <h1
                className="text-2xl d-none d-md-block animate-dots"
                style={{ fontFamily: "'Dosis', sans-serif" }}
              >
                Process Anything
              </h1>

              <ul
                className="m-0 pt-2 pb-2 pe-0 ps-0 mb-2 mb-md-0 shadow"
                style={{
                  listStyleType: "none",
                  backgroundColor: "white",
                  borderRadius: "20px",
                }}
              >
                <li>
                  <form
                    onSubmit={handleYoutubeUrl}
                    className="d-flex align-items-center justify-content-center"
                  >
                    <input
                      required
                      className="form-control w-50"
                      style={{ padding: "2px", margin: "4px" }}
                      onChange={(e) => setYoutubeUrl(e.target.value)}
                      type="text"
                      value={youtubeUrl}
                      placeholder="Enter Youtube Video Url."
                    />
                    <button
                      className="submitbutton d-flex align-items-center justify-content-center"
                      type="submit"
                    >
                      {loading.youtubeUrl ? (
                        <div className="Spinner"></div>
                      ) : null}
                      Submit
                    </button>
                  </form>
                </li>
                <li>
                  <form onSubmit={handleFileUpload}>
                    <div className="d-flex align-items-center justify-content-center">
                      <input
                        required
                        type="file"
                        onChange={(e) => {
                          setSelectedFile(e.target.files[0]);
                        }}
                        className="form-control w-50 m-1"
                        id="fileInput"
                      />

                      <button
                        className="submitbutton d-flex align-items-center justify-content-center"
                        type="submit"
                      >
                        {loading.pdfUrl ? (
                          <div className="Spinner"></div>
                        ) : null}
                        Upload
                      </button>
                    </div>
                  </form>
                </li>
                <li>
                  <form
                    onSubmit={handleWebUrl}
                    className="d-flex align-items-center justify-content-center"
                  >
                    <input
                      required
                      className="form-control w-50"
                      style={{ padding: "2px", margin: "4px" }}
                      onChange={(e) => setWebUrl(e.target.value)}
                      type="text"
                      value={webUrl}
                      placeholder="Enter Website Url."
                    />
                    <button
                      className="submitbutton d-flex align-items-center justify-content-center"
                      type="submit"
                    >
                      {loading.webUrl ? <div className="Spinner"></div> : null}
                      Submit
                    </button>
                  </form>
                </li>
              </ul>
            </div>

            <div
              className="col-md-7 col-lg-8 shadow py-1 px-1"
              style={{ backgroundColor: "white", borderRadius: "20px" }}
            >
              <div className="">
                <div>
                  <div>
                    <div className="chatbot">
                      <header>
                        <h2>TexMin Chatbot</h2>
                        <h5>Powered by Vyomchara</h5>
                      </header>
                      <ul className="chatbox">
                        <li id="chatli" className="chat incoming">
                          <p>How can I help you today?</p>
                        </li>
                      </ul>
                      <div className="chat-input">
                        <textarea
                          placeholder="Enter a message..."
                          spellCheck="false"
                          required
                          value={messages}
                          onChange={handleInputChange}
                          onKeyDown={handleInputKeyDown}
                        />
                        <span onClick={handleChat} id="send-btn" className="">
                          <SendHorizontal strokeWidth={0} fill="#01000DCC" />
                        </span>
                      </div>
                    </div>
                    <ul
                      style={{
                        listStyleType: "none",
                        padding: 0,
                        display: "flex",
                        margin: 0,
                        marginTop: 0,
                      }}
                    >
                      <li
                        style={{
                          marginRight: "10px",
                          marginLeft: "10px",
                          marginBottom: "10px",
                        }}
                      >
                        <button
                          className="submitbutton"
                          onClick={handleSpeechRecognition}
                        >
                          {isListening ? "Listening..." : "Push To Talk"}
                        </button>
                      </li>
                      {firstAnswerGenerated && (
                        <li>
                          <button
                            className="submitbutton"
                            onClick={toggleAudioPlayback}
                          >
                            {isAudioPlaying ? "Pause Audio" : "Play Audio"}
                          </button>
                        </li>
                      )}
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
};

export default Chatbot;
