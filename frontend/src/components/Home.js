import React from 'react';
import { Link } from 'react-router-dom';

function Home() {
  return (
    <div className="container mt-5">
      <div className="jumbotron">
        <h1 className="display-4">Welcome to the Gifting Recommendation Platform</h1>
        <p className="lead">Find the perfect gift for your loved ones with our intelligent recommendation system.</p>
        <hr className="my-4" />
        <p>Sign up now to start creating recipient profiles and managing your gifting events.</p>
        <Link to="/signup" className="btn btn-primary btn-lg">Get Started</Link>
      </div>

      <div className="row mt-5">
        <div className="col-md-4">
          <h3>Create Recipient Profiles</h3>
          <p>Add detailed information about your gift recipients to get personalized recommendations.</p>
        </div>
        <div className="col-md-4">
          <h3>Manage Events</h3>
          <p>Keep track of upcoming gifting occasions and set budgets for each event.</p>
        </div>
        <div className="col-md-4">
          <h3>Get Smart Recommendations</h3>
          <p>Receive tailored gift suggestions based on recipient preferences and your budget.</p>
        </div>
      </div>
    </div>
  );
}

export default Home;
