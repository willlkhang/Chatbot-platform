"use client";

import { useState } from "react";
import Image from "next/image"

export default function LoginPage() {
  
    const [username, setUsername] = useState("");
    const [password, setPassword] = useState("");
    const [errors, setErrors] = useState({});
    const [loading, setLoading] = useState(false);

    const clientCredentials = btoa("project:secret");

    const handleSubmit = async () => {
        if (loading) return;

        const { isValid, errors } = validateLogin(username, password);

        if (!isValid){
            setErrors(errors);
            return;
        }
        setLoading(true);

        try {
            // Match the working Postman request: x-www-form-urlencoded to /oauth2/token
            const formBody = new URLSearchParams({
                username,
                password,
                grant_type: "password",
            }).toString();

            const result = await fetch("http://localhost:8060/api/authen/oauth2/token", {
                method: "POST",
                headers: { 
                    "Content-Type": "application/x-www-form-urlencoded",
                    "Accept": "application/json",
                    "Authorization": `Basic ${clientCredentials}`,
                },
                body: formBody,
            });

            if (result.ok) {
                const res = await result.json();
                localStorage.setItem("accessToken", res.access_token); // store token access to local storage, however, this token has expired time
                window.dispatchEvent(new Event("accessTokenChanged"));
                window.location.href = "/"; //redirection to home page
            } else {
                const errText = await result.text().catch(() => "");
                setErrors({
                    general:
                        errText?.trim()
                            ? `Login failed: ${errText}`
                            : "Invalid username or password",
                });
            }
        } catch(e) {
            console.error("Fetch Error:", e);
            setErrors({ general: "Network error. Please check your connection or CORS settings." });
        } finally {
            setLoading(false);
        }
    };

    const validateLogin = (uName, pWord) => {
        const errs = {};
        if (!uName.trim()) errs.username = "Username cannot be empty";
        if (!pWord.trim()) errs.password = "Password cannot be empty";
        return { isValid: Object.keys(errs).length === 0, errors: errs };
    };

    return (
        <div className="login-container">
            <div className="login-banner">
                <Image
                    src={ "/login/banner.jpg" ??  "/error/error.png" }
                    alt={ "/error/error.png" }
                    fill
                />
            </div>
            <div className="login-card">
                <div className="login-header">
                    <h1>Login</h1>
                    <p>Sign in to your account</p>
                </div>

                {errors.general && <p className="error-message-general">{errors.general}</p>}

                <div className="login-form">
                    <div className="input-group">
                        <input
                            type="text"
                            placeholder="Username"
                            value={username}
                            onChange={(e) => setUsername(e.target.value)}
                            className={errors.username ? "input-error" : ""}
                        />

                        {errors.username && <span className="error-text">{errors.username}</span>}
                    </div>

                   <div className="input-group">
                        <input
                            type="password"
                            placeholder="Password"
                            value={password}
                            onChange={(e) => setPassword(e.target.value)}
                            className={errors.password ? "input-error" : ""}
                        />

                        {errors.password && <span className="error-text">{errors.password}</span>}
                    </div>

                    <button
                        onClick={handleSubmit}
                        disabled={loading}
                        className="login-submit-btn"
                    >
                        {loading ? "Processing..." : "Login"}
                    </button>

                    <div className="login-footer">
                        Do not have an account? <span>Reset Password</span>
                    </div>

                </div>  
            </div>
        </div>
    );
}