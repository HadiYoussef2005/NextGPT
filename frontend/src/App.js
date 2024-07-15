import React, { useState, useRef, useEffect } from 'react';
import axios from 'axios';
import './App.css';

function App() {
  const [input, setInput] = useState('');
  const [output, setOutput] = useState('');
  const outputRef = useRef(null);

  useEffect(() => {
    outputRef.current.scrollTop = outputRef.current.scrollHeight;
  }, [output]);

  const handleChange = (e) => {
    setInput(e.target.value);
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      handleSubmit();
    }
  };

  const clearConversation = async () => {
    try {
      await axios.post('http://127.0.0.1:8000/clear_conversation/');
      setOutput('');
    } catch (error) {
      console.error("Error:", error);
    }
  };

  const handleSubmit = async () => {
    try {
      const response = await axios.post('http://127.0.0.1:8000/chatbot_query/', { input_data: input });
      setOutput(prevOutput => `${prevOutput}\nUser: ${input}\nNextGPT: ${response.data.output}`);
      setInput('');
    } catch (error) {
      console.error('Error:', error);
    }
  };

  return (
    <div className="app-container">
      <div className="output" ref={outputRef}>
        {output.split('\n').map((line, index) => (
          <div key={index}>{line}</div>
        ))}
      </div>
      <div className="container">
        <div className="input-column">
          <input className="input-field" type="text" value={input} onChange={handleChange} onKeyPress={handleKeyPress} />
        </div>
        <div className="buttons-column">
          <button className="button" onClick={handleSubmit}>Submit</button>
          <button className="button" onClick={clearConversation}>Clear Conversation</button>
        </div>
      </div>
    </div>
  );
}

export default App;
