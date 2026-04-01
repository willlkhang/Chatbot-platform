import "./styles/global.scss";
import "./styles/main.scss";

import Header from "./components/header/Header";

export default function RootLayout({ 
  children, 
}: Readonly <{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>
        
        <div className="main-layout">
          <Header />
          {children}
        </div>
        
      </body>
    </html>
  );
}