import React from "react";
import "./animated-map.css";

const LoaderOne = () => {
  return (
    <div className="loader-wrapper">
      <div className="loader" />
    </div>
  );
};

const LoaderTwo = () => {
  return (
    <div className="center-body">
      <div className="loader-shape-3" />
    </div>
  );
};

export { LoaderOne, LoaderTwo };
