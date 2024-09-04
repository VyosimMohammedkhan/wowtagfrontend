import React, {useEffect, useState} from "react";
import axios from "axios";
import "bootstrap-icons/font/bootstrap-icons.css";
import "bootstrap/dist/css/bootstrap.css";


function Tags() {
	const [domain, setDomain] = useState("");
	const [loading, setLoading] = useState(false);
	const [tags, setTags] = useState({});
	const [meta, setMeta] = useState({keywords: "", description: ""});

	const getTags = async () => {
		setLoading(true);
		try {
			console.log("calling for ", domain);
			const result = await axios.post("http://localhost:8000/extract_keywords", {domain: domain});

			console.log(result);
			const tags = result.data[0].tags;
			const meta = {keywords: result.data[0].keywords, description: result.data[0].description};
			setMeta(meta);
			setTags(tags);
		} catch (error) {
			console.log(error);
		}
		setLoading(false);
	};

	const handleClick = () => {
		getTags();
	};

	return (
		<div className="container">
			<nav className="row">
				{loading ? (
					<div class="spinner-border m-5" role="status">
						<span class="visually-hidden">Loading...</span>
					</div>
				) : (
					<div className="col-sm-3 d-flex align-items-center">
						<div className="input-group">
							<input type="text" className="form-control" placeholder="Enter Company Website" aria-label="domain" onChange={e => setDomain(e.target.value)} />
							<button className="btn btn-info" onClick={handleClick}>
								Find Tags
							</button>
						</div>
					</div>
				)}
			</nav>
			<div className="d-flex align-items-start justify-content-start flex-column ">
				<div className="d-flex align-items-start flex-column">
					<h4>Keywords</h4>
					<p align="left">{meta.keywords}</p>
				</div>
				<div>
					<div className="d-flex align-items-start flex-column">
						<h4>Description</h4>
						<p align="left">{meta.description}</p>
					</div>

					<h4 align="left">Tags</h4>
					<div className="d-flex align-items-center flex-wrap" >
						{Object.entries(tags).map(([key, value]) => (
							<span className="badge bg-info m-1 p-2" style={{ fontSize: `${parseInt(Math.floor(value*100))+10}px` }}>{key}</span>
						))}
					</div>

					
					{/* 
				<h4>Bigram Tags</h4>
				<div className="d-flex align-items-start">		
					{tags.bi.map(c => (
						<span className="badge rounded-pill bg-secondary m-1 p-2">{c}</span>
					))}
				</div>

				<h4>Trigram Tags</h4>
				<div className="d-flex align-items-start">
					{tags.tri.map(c => (
						<span className="badge rounded-pill bg-secondary m-1 p-2">{c}</span>
					))}
				</div> */}
				</div>
			</div>
		</div>
	);
}

export default Tags;
