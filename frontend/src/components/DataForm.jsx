import React, { useState } from "react";
// import Results from "./Results";

function DataForm() {
  const [inputs, setInputs] = useState({});
  const [queryArray, setqueryArray] = useState([]);

  const handleChange = (e) => {
    const target = e.target;
    const value = target.type === "checkbox" ? target.checked : target.value;
    const name = target.name;
    setInputs((values) => ({ ...values, [name]: value }));
    console.log(inputs);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const response = await fetch("http://127.0.0.1:8000/data", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(inputs),
    });
    const result = await response.json();

    console.log(result.data);
    setqueryArray(result.data);
  };

  return (
    <>
      <form onSubmit={handleSubmit}>
        <label>
          Enter your name:
          <input
            type="text"
            name="jobTitle"
            value={inputs.jobTitle || ""}
            onChange={handleChange}
          />
        </label>
        {/* <p>Current value: {jobTitle}</p> */}

        <label>
          Full Time:
          <input
            type="checkbox"
            name="fullTime"
            checked={inputs.fullTime || false}
            onChange={handleChange}
          />
        </label>

        <label>
          Part Time:
          <input
            type="checkbox"
            name="partTime"
            checked={inputs.partTime || false}
            onChange={handleChange}
          />
        </label>

        <label>
          Contract Time:
          <input
            type="checkbox"
            name="contract"
            checked={inputs.contract || false}
            onChange={handleChange}
          />
        </label>

        <label>
          Intern:
          <input
            type="checkbox"
            name="internship"
            checked={inputs.internship || false}
            onChange={handleChange}
          />
        </label>
        <button type="submit">Submit</button>
      </form>
      {queryArray.length > 0 &&
        queryArray.map((value, index) => <p key={index}>{value}</p>)}
    </>
  );
}

export default DataForm;
