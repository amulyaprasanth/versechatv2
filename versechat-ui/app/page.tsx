import Navbar from "./navbar/Navbar";


export default function Home() {
  return (
    <div className="h-screen flex flex-col overflow-hidden">
      <header className="shrink-0">
        <Navbar />
      </header>

      <main className="flex-1 min-h-0">
      </main>
    </div>
  );
}