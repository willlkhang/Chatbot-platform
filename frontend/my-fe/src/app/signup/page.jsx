"use client";

import { useRouter } from "next/navigation";
import { useMemo, useState } from "react";
import Image from "next/image";

export default function SignupPage() {
  const router = useRouter();

  const API_GATEWAY = process.env.NEXT_PUBLIC_API_GATEWAY || "http://localhost:8060";

  const [form, setForm] = useState({
    fullName: "",
    username: "",
    email: "",
    phone: "",
    password: "",
    confirmPassword: "",
  });

  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);

  const bannerSrc = useMemo(() => "/login/banner.jpg", []);

  const onChange = (key) => (e) => {
    const value = e.target.value;
    setForm((prev) => ({ ...prev, [key]: value }));
  };

  const validate = () => {
    const errs = {};
    if (!form.fullName.trim()) errs.fullName = "Full name cannot be empty";
    if (!form.username.trim()) errs.username = "Username cannot be empty";
    if (!form.email.trim()) errs.email = "Email cannot be empty";
    if (!/^\S+@\S+\.\S+$/.test(form.email.trim())) errs.email = "Email format is invalid";
    if (!form.phone.trim()) errs.phone = "Phone cannot be empty";
    if (!form.password) errs.password = "Password cannot be empty";
    if (form.password.length < 6) errs.password = "Password must be at least 6 characters";
    if (form.confirmPassword !== form.password) errs.confirmPassword = "Passwords do not match";
    return errs;
  };

  const handleSubmit = async () => {
    if (loading) return;
    const errs = validate();
    if (Object.keys(errs).length) {
      setErrors(errs);
      return;
    }

    setLoading(true);
    setErrors({});

    try {
      const payload = {
        username: form.username.trim(),
        email: form.email.trim(),
        password: form.password,
        phone: form.phone.trim(),
        fullName: form.fullName.trim(),
      };

      const res = await fetch(`${API_GATEWAY}/api/user/registery`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Accept: "application/json, text/plain",
        },
        body: JSON.stringify(payload),
      });

      const contentType = res.headers.get("content-type") || "";
      const body = contentType.includes("application/json") ? await res.json() : await res.text();

      if (!res.ok) {
        setErrors({
          general: typeof body === "string" && body.trim() ? body : "Signup failed. Please try again.",
        });
        return;
      }

      // Backend returns either a user object or a string message.
      if (typeof body === "string") {
        const msg = body.trim();
        if (msg && /already/i.test(msg)) {
          setErrors({ general: msg });
          return;
        }
      }

      router.push("/login");
    } catch (e) {
      console.error("Signup Error:", e);
      setErrors({ general: "Network error. Please check your connection or CORS settings." });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="signup-container">
      <div className="signup-banner">
        <Image src={bannerSrc} alt="signup banner" fill />
      </div>

      <div className="signup-card">
        <div className="signup-header">
          <h1>Sign Up</h1>
          <p>Create your account</p>
        </div>

        {errors.general && <p className="error-message-general">{errors.general}</p>}

        <div className="signup-form">
          <div className="input-group">
            <input
              type="text"
              placeholder="Full name"
              value={form.fullName}
              onChange={onChange("fullName")}
              className={errors.fullName ? "input-error" : ""}
            />
            {errors.fullName && <span className="error-text">{errors.fullName}</span>}
          </div>

          <div className="input-group">
            <input
              type="text"
              placeholder="Username"
              value={form.username}
              onChange={onChange("username")}
              className={errors.username ? "input-error" : ""}
            />
            {errors.username && <span className="error-text">{errors.username}</span>}
          </div>

          <div className="input-group">
            <input
              type="email"
              placeholder="Email"
              value={form.email}
              onChange={onChange("email")}
              className={errors.email ? "input-error" : ""}
            />
            {errors.email && <span className="error-text">{errors.email}</span>}
          </div>

          <div className="input-group">
            <input
              type="tel"
              placeholder="Phone"
              value={form.phone}
              onChange={onChange("phone")}
              className={errors.phone ? "input-error" : ""}
            />
            {errors.phone && <span className="error-text">{errors.phone}</span>}
          </div>

          <div className="input-group">
            <input
              type="password"
              placeholder="Password"
              value={form.password}
              onChange={onChange("password")}
              className={errors.password ? "input-error" : ""}
            />
            {errors.password && <span className="error-text">{errors.password}</span>}
          </div>

          <div className="input-group">
            <input
              type="password"
              placeholder="Confirm password"
              value={form.confirmPassword}
              onChange={onChange("confirmPassword")}
              className={errors.confirmPassword ? "input-error" : ""}
            />
            {errors.confirmPassword && (
              <span className="error-text">{errors.confirmPassword}</span>
            )}
          </div>

          <button onClick={handleSubmit} disabled={loading} className="signup-submit-btn">
            {loading ? "Creating..." : "Create account"}
          </button>

          <div className="signup-footer">
            Already have an account?{" "}
            <span role="button" tabIndex={0} onClick={() => router.push("/login")}>
              Login
            </span>
          </div>
        </div>
      </div>
    </div>
  );
}

