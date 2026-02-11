import { useEffect, useState } from "react";

function PlantList() {
  const [plants, setPlants] = useState([]);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/plants")
      .then(res => res.json())
      .then(data => setPlants(data))
      .catch(err => console.log(err));
  }, []);

  return (
    <div style={{ maxWidth: "400px", margin: "0 auto" }}>
      <h2>Bitki Listesi</h2>

      {plants.map(plant => (
        <div key={plant.id}>
            <h3>{plant.name}</h3>
            <img
            src={`http://127.0.0.1:8000${plant.image}`}
            alt={plant.name}
            style={{
              width: "100%",
              height: "400px",
              objectFit: "cover",
              borderRadius: "10px"
            }}
          />
          <p>Boyu: {plant.size_cm}</p>
          <hr />
        </div>
      ))}
    </div>
  );
}

export default PlantList;
