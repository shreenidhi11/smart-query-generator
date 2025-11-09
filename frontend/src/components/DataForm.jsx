import React, { useState } from "react";
// import Results from "./Results";
import "./DataForm.css";

function DataForm() {
  const [inputs, setInputs] = useState({});
  const [queryArray, setqueryArray] = useState([]);
  const [alternateTitles, setalternateTitles] = useState([]);
  const [loading, setloading] = useState(false);

  const handleChange = (e) => {
    const target = e.target;
    const value = target.type === "checkbox" ? target.checked : target.value;
    const name = target.name;
    setInputs((values) => ({ ...values, [name]: value }));
    console.log(inputs);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setloading(true);
    const response = await fetch("http://127.0.0.1:8000/data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(inputs),
    });
    const result = await response.json();

    // console.log(result.data);
    // console.log(result.additional_job_titles);
    setqueryArray(result.data);
    setalternateTitles(result.additional_job_titles);
    setloading(false);
  };

  const openLinkedIn = (query) => {
    const encoded = encodeURIComponent(query);
    window.open(
      `https://www.linkedin.com/search/results/content/?keywords=${encoded}&origin=FACETED_SEARCH&sortBy=%22date_posted%22`,
      "_blank"
    );
  };

  const openGoogle = (query) => {
    const encoded = encodeURIComponent(query);
    window.open(
      `https://www.google.com/search?q=${encoded}&tbs=qdr:d`,
      "_blank"
    );
  };
  return (
    <div className="container">
      <h2 className="title">QueryCraft</h2>
      <h2 className="title2">Job Query Optimizer</h2>
      <form onSubmit={handleSubmit} className="form">
        <div className="input-group">
          <label>Enter job title:</label>
          <input
            type="text"
            name="jobTitle"
            value={inputs.jobTitle || ""}
            onChange={handleChange}
            placeholder="e.g. Software Engineer"
          />
        </div>

        {/* <div className="checkbox-group">
          {["fullTime", "partTime", "contract", "internship"].map((type) => (
            <label key={type}>
              <input
                type="checkbox"
                name={type}
                checked={inputs[type] || false}
                onChange={handleChange}
              />
              {type.charAt(0).toUpperCase() +
                type.slice(1).replace("Time", " Time")}
            </label>
          ))}
        </div> */}

        <button type="submit" className="btn-primary">
          Generate Queries
        </button>
      </form>

      <div className="results">
        {loading && <p>Loading...</p>}
        {!loading &&
          queryArray.length > 0 &&
          queryArray.map((value, index) => (
            <div key={index} className="query-item">
              <p className="query-text">{value}</p>
              <div className="button-group">
                <button
                  className="btn-secondary"
                  onClick={() => navigator.clipboard.writeText(value)}
                >
                  Copy
                </button>
                <button
                  className="btn-linkedin"
                  onClick={() => openLinkedIn(value)}
                >
                  Go to LinkedIn
                </button>
                <button
                  className="btn-google"
                  onClick={() => openGoogle(value)}
                >
                  Go to Google
                </button>
              </div>
            </div>
          ))}
      </div>
      {/* {alternateTitles.length > 0 && (
        <p className="suggestions">Related Roles You Can Try</p>
      )} */}
      {!loading && queryArray.length > 0 && (
        <p className="suggestions">Explore Similar Jobs</p>
      )}
      <div className="alternate-titles">
        {!loading &&
          queryArray.length > 0 &&
          alternateTitles.map((value, index) => (
            <p key={index} className="alt-title">
              {value}
            </p>
          ))}
      </div>
    </div>
  );
}

export default DataForm;
