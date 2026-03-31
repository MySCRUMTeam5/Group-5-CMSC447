import { useState } from "react";

function ProfilePage({ navigate }) {
  const [isEditing, setIsEditing] = useState(false);

  const [profile, setProfile] = useState({
    username: "Username",
    email: "email@example.com",
    bio: "Biography info",
    profile_picture: ""
  });

  const [formData, setFormData] = useState(profile);

  const handleEditClick = () => {
    setIsEditing(true);
  };

  const handleCancelClick = () => {
    setFormData(profile);
    setIsEditing(false);
  };

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData({
      ...formData,
      [name]: value
    });
  };

  const handleSaveClick = () => {
    setProfile(formData);
    setIsEditing(false);
  };

  return (
    <div style={styles.page}>
      <div style={styles.card}>
        <button style={styles.cancelButton} onClick={() => navigate('home')}>
            Back to Home
        </button>
        <div style={styles.imageSection}>
          {profile.profile_picture ? (
            <img
              src={profile.profile_picture}
              alt="Profile"
              style={styles.image}
            />
          ) : (
            <div style={styles.placeholderImage}>No Image</div>
          )}
        </div>

        {!isEditing ? (
          <>
            <h1 style={styles.username}>{profile.username}</h1>
            <p style={styles.email}>{profile.email}</p>

            <div style={styles.infoBox}>
              <h3>Bio</h3>
              <p>{profile.bio || "No bio added yet."}</p>
            </div>

            <button style={styles.button} onClick={handleEditClick}>
              Edit Profile
            </button>
          </>
        ) : (
          <>
            <h1 style={styles.username}>Edit Profile</h1>

            <label style={styles.label}>Username</label>
            <input
              type="text"
              name="username"
              value={formData.username}
              onChange={handleChange}
              style={styles.input}
            />

            <label style={styles.label}>Email</label>
            <input
              type="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              style={styles.input}
            />

            <label style={styles.label}>Bio</label>
            <textarea
              name="bio"
              value={formData.bio}
              onChange={handleChange}
              style={styles.textarea}
            />

            <div style={styles.buttonRow}>
              <button style={styles.button} onClick={handleSaveClick}>
                Save
              </button>
              <button style={styles.cancelButton} onClick={handleCancelClick}>
                Cancel
              </button>
            </div>
          </>
        )}
      </div>
    </div>
  );
}

const styles = {
  page: {
    minHeight: "100vh",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    backgroundColor: "#f4f4f4",
    padding: "20px"
  },
  card: {
    backgroundColor: "#ffffff",
    padding: "30px",
    borderRadius: "12px",
    boxShadow: "0 4px 12px rgba(0, 0, 0, 0.1)",
    width: "100%",
    maxWidth: "500px",
    textAlign: "center"
  },
  imageSection: {
    marginBottom: "20px"
  },
  image: {
    width: "120px",
    height: "120px",
    borderRadius: "50%",
    objectFit: "cover"
  },
  placeholderImage: {
    width: "120px",
    height: "120px",
    borderRadius: "50%",
    backgroundColor: "#ddd",
    display: "flex",
    justifyContent: "center",
    alignItems: "center",
    margin: "0 auto",
    fontWeight: "bold",
    color: "#666"
  },
  username: {
    marginBottom: "10px"
  },
  email: {
    marginBottom: "20px",
    color: "#666"
  },
  infoBox: {
    textAlign: "left",
    marginBottom: "20px",
    padding: "15px",
    backgroundColor: "#f9f9f9",
    borderRadius: "8px"
  },
  label: {
    display: "block",
    textAlign: "left",
    marginBottom: "6px",
    marginTop: "12px",
    fontWeight: "bold"
  },
  input: {
    width: "100%",
    padding: "10px",
    marginBottom: "10px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    fontSize: "14px"
  },
  textarea: {
    width: "100%",
    padding: "10px",
    minHeight: "100px",
    borderRadius: "6px",
    border: "1px solid #ccc",
    fontSize: "14px",
    marginBottom: "15px"
  },
  buttonRow: {
    display: "flex",
    justifyContent: "center",
    gap: "10px"
  },
  button: {
    padding: "10px 16px",
    border: "none",
    borderRadius: "6px",
    backgroundColor: "#2563eb",
    color: "white",
    cursor: "pointer"
  },
  cancelButton: {
    padding: "10px 16px",
    border: "none",
    borderRadius: "6px",
    backgroundColor: "#888",
    color: "white",
    cursor: "pointer"
  }
};

export default ProfilePage;