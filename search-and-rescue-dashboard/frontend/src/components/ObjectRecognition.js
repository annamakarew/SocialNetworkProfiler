import React from 'react';

const ObjectRecognition = ({ data }) => {
  return (
    <div className="object-recognition">
      <h2>Object Recognition</h2>
      <div className="image-gallery">
        {data.map((item, index) => (
          <div key={index} className="image-card">
            <img src={item.imageUrl} alt={`Detected objects ${index}`} />
            <p>Objects: {item.objects.join(', ')}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ObjectRecognition;
