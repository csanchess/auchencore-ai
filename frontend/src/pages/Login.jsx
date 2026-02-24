import { useState, useContext } from "react";
import { useNavigate } from "react-router-dom";
import { AuthContext } from "../auth/AuthContext";

export default function Login() {
  const { login } = useContext(AuthContext);
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [isRegistering, setIsRegistering] = useState(false);
  const [error, setError] = useState("");

  const API_URL = import.meta.env.VITE_API_URL;

  const handleSubmit = async () => {
    setError("");

    const endpoint = isRegistering ? "/auth/register" : "/auth/login";

    try {
      const response = await fetch(`${API_URL}${endpoint}`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ email, password }),
      });

      if (!response.ok) {
        throw new Error("Authentication failed");
      }

      const data = await response.json();

      // If registering, immediately log in after
      if (isRegistering) {
        const loginRes = await fetch(`${API_URL}/auth/login`, {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ email, password }),
        });

        const loginData = await loginRes.json();
        login(loginData.access_token);
      } else {
        login(data.access_token);
      }

      navigate("/app");
    } catch (err) {
      setError("Invalid credentials or server error.");
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-bg text-white px-6">

      <div className="w-full max-w-md space-y-8">

        {/* Branding */}
        <div className="text-center space-y-3">
          <h1 className="text-3xl font-semibold text-accent">
            AuchenCore AI
          </h1>
          <p className="text-gray-400 text-sm">
            unlocking the Massive Power within your mind
          </p>
        </div>

        {/* Card */}
        <div className="bg-card border border-border rounded-2xl p-8 space-y-6 shadow-lg">

          <h2 className="text-xl font-medium text-center">
            {isRegistering ? "Create Account" : "Sign In"}
          </h2>

          {error && (
            <div className="text-red-400 text-sm text-center">
              {error}
            </div>
          )}

          <div className="space-y-4">
            <input
              type="email"
              placeholder="Email"
              className="w-full bg-bg border border-border rounded-lg px-4 py-3 focus:outline-none focus:ring-1 focus:ring-accent"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
            />

            <input
              type="password"
              placeholder="Password"
              className="w-full bg-bg border border-border rounded-lg px-4 py-3 focus:outline-none focus:ring-1 focus:ring-accent"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
            />
          </div>

          <button
            onClick={handleSubmit}
            className="w-full bg-accent hover:opacity-90 transition rounded-lg py-3 font-medium"
          >
            {isRegistering ? "Register" : "Login"}
          </button>

          <div className="text-center text-sm text-gray-400">
            {isRegistering ? "Already have an account?" : "No account yet?"}{" "}
            <button
              onClick={() => setIsRegistering(!isRegistering)}
              className="text-accent hover:underline"
            >
              {isRegistering ? "Sign in" : "Create one"}
            </button>
          </div>

        </div>

      </div>
    </div>
  );
}