import React, { useEffect, useState } from 'react';
import axios from 'axios';

const ObjectRecognition = () => {
  const [images, setImages] = useState([]);

  useEffect(() => {
    axios.get('/api/object-recognition')
      .then(response => setImages(response.data))
      .catch(error => console.error('Error fetching object recognition data:', error));
  }, []);

  return (
    <div className="object-recognition">
      <h2>Object Recognition</h2>
      <div className="image-gallery">
        {images.map((image, index) => (
          <div key={index} className="image-card">
            <img src={image.url} alt={`Object ${index}`} />
            <p>Objects: {image.objects.join(', ')}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ObjectRecognition;
