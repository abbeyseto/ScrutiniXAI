"use client"; // This is a client component 👈🏽
import "core-js/stable";
import "regenerator-runtime/runtime";
import { FaStop, FaMicrophone } from 'react-icons/fa';
import { useState, useEffect, ChangeEvent } from 'react';
import SpeechRecognition, { useSpeechRecognition } from 'react-speech-recognition';
import axios from 'axios';

const IndexPage = () => {
  const [isRecording, setIsRecording] = useState(false);
  const [isuploading, setIsUploading] = useState(false);
  const [transcript, setTranscript] = useState('');
  const [questions, setQuestions] = useState([]);
  const [jobDescriptionFile, setJobDescriptionFile] = useState<File | null>(null);
  const [cvFile, setCvFile] = useState<File | null>(null);
  const { transcript: finalTranscript, resetTranscript } = useSpeechRecognition();
  const [credAnalysis, setCredAnalysis] = useState({
    "jobDescriptionSummary": [],
    "cvSummary": [],
    "analysis": []
  });

  useEffect(() => {
    if (finalTranscript) {
      setTranscript(finalTranscript);
    }
  }, [finalTranscript]);

  useEffect(() => {
    const interval = setInterval(() => {
      if (transcript) {
        console.log('transcript', transcript);
        generateQuestions(transcript).then((data) => {
          setQuestions(data.questions);
        });
      }
    }, 10000);

    return () => clearInterval(interval);
  }, [transcript]);

  const handleJobDescriptionFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setJobDescriptionFile(file || null);
  };

  const handleCvFileChange = (event: ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    setCvFile(file || null);
  };

 
  const startRecording = () => {
    resetTranscript();
    setIsRecording(true);
    SpeechRecognition.startListening({ continuous: true });
  };

  const stopRecording = () => {
    setIsRecording(false);
    SpeechRecognition.stopListening();
    console.log("finalTranscript", finalTranscript);
    resetTranscript();
    setTranscript('');
    
  };

  const handleSubmit = () => {
    if (!jobDescriptionFile || !cvFile) {
      // Handle the case where files are not selected
      return;
    }
    setIsUploading(true);
    const formData = new FormData();
    formData.append('job_description_file', jobDescriptionFile);
    formData.append('cv_file', cvFile);

    fetch('http://localhost:8000/get-job-description-and-cv', {
      method: 'POST',
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        // Handle the response from the server
        console.log(data);
        setCredAnalysis(data);
        setIsUploading(false);
      })
      .catch((error) => {
        // Handle any errors
        console.error(error);
      });
  };


  const generateQuestions = async (context: string) => {
    // read job description from local txt file
    console.log("finalTranscript", finalTranscript);
    const job_description = await fetch('http://localhost:8000/get-job-description-local').then((response) => response.text());
    const response = await axios.post('http://localhost:8000/generate-questions', { context, job_description });
    return response.data;
  };

  return (
    <main className="max-w-7xl mx-auto py-10">
      <h1 className="text-4xl font-bold mb-5">ScrutiniX</h1>
      <p className="text-lg mb-5">
        Welcome to ScrutiniX, an AI Interview Assistant! This tool will help you assess your candidate during their job interview by generating potential interview
        questions based on your conversation with them and the job description.
      </p>
      <div className="w-full flex flex-row py-4 h-28 md:flex-row md:space-x-10 flex-grow-1 ">
        {/* button to start conversation  */}
        <button
          onClick={isRecording ? stopRecording : startRecording}
          className={`py-2 px-4 rounded font-bold text-white ${isRecording ? 'bg-red-500 hover:bg-red-700' : 'bg-green-500 hover:bg-green-700'
            }`}
        >
          {isRecording ? (
            <>
              <FaStop className="inline-block mr-2" />
              Stop Interview
            </>
          ) : (
            <>
              <FaMicrophone className="inline-block mr-2" />
              Start Interview
            </>
          )}
        </button>
        {/* Column 1: Upload Job Description and CV */}

        {/* Job Description Upload */}
        <div className="justify-center">
          <label htmlFor="jobDescription" className="block font-bold">
            Job Description:
          </label>
          <input
            type="file"
            id="jobDescription"
            className="border border-gray-300 py-2 px-3 rounded-md shadow-sm"
            onChange={handleJobDescriptionFileChange}
          />
        </div>

        {/* CV Upload */}
        <div className="justify-center">
          <label htmlFor="cv" className="block font-bold">
            CV:
          </label>
          <input
            type="file"
            id="cv"
            className="border border-gray-300 py-2 px-3 rounded-md shadow-sm"
            onChange={handleCvFileChange}
          />
        </div>

        {/* Submit Button */}
        <button
          className="bg-blue-500 hover:bg-blue-700 text-white font-bold px-4 mt-6 rounded h-12"
          onClick={handleSubmit}
        >
          {isuploading ? "Uploading" : "Submit"}
        </button>
      </div>

      <div className="flex flex-col">
        {/* First Row */}
        <div className="flex flex-col md:flex-row md:space-x-10 flex-grow-1">
          {/* Column 2: Suggested Questions */}
          <div className="w-full md:w-2/6">
            <div className="w-full">
              <h2 className="text-2xl font-bold mb-4">Suggested Questions</h2>
              <ul className="bg-white p-4 rounded-md shadow-sm">
                {questions.map((question, index) => (
                  <li key={index} className="mb-2">
                    {question}
                  </li>
                ))}
              </ul>
            </div>
          </div>

          {/* Column 3: User Match Analysis */}
          <div className="w-full md:w-4/6">
            {/* User Match Analysis */}
            <div className="flex flex-col md:flex-row md:space-x-10">
              <div className="flex flex-row w-full space-x-10 items-start">
                <div className="bg-white rounded-md shadow p-4 w-1/3">
                  <h3 className="text-2xl font-bold mb-4">Analysis</h3>
                  {credAnalysis?.analysis && credAnalysis?.analysis?.map((item: string, index: number) => (
                    item.length > 1 && <div key={index} className="">
                      <p key={item} className="">
                        {item}
                      </p>
                    </div>
                  ))}
                </div>
                
                <div className="bg-white rounded-md shadow p-4 w-1/3">
                  <h3 className="text-2xl font-bold mb-4">JD Summary</h3>
                  {credAnalysis?.analysis && credAnalysis?.jobDescriptionSummary?.map((item: string, index: number) => (
                    item.length > 1 && <div key={index} className="">
                      <p key={item} className="">
                        {item}
                      </p>
                    </div>
                  ))} </div>
                
                <div className="bg-white rounded-md shadow p-4 w-1/3">
                  <h3 className="text-2xl font-bold mb-4">CV Summary</h3>
                  {credAnalysis?.analysis && credAnalysis?.cvSummary?.map((item: string, index: number) => (
                    item.length > 1 && <div key={index} className="">
                      <p key={item} className="">
                        {item}
                      </p>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Second Row */}
        <div className="h-1/4">
          <div className="w-full">
            <h2 className="text-2xl font-bold mb-4">Transcript</h2>
            <p className="bg-white p4 rounded-md shadow-sm">{transcript}</p>
          </div>
        </div>
      </div>
    </main>
  );
};


export default IndexPage;
