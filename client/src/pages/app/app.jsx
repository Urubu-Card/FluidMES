import { Outlet } from 'react-router-dom';
import Sidebar from '../components/Sidebar/sideBar.jsx'; 

export default function App() {
    return (
        <div style={{ display: 'flex', height: '100vh', width: '100vw' }}>
            {/* SIDEBAR */}
            <Sidebar />

            {/* CONTENT */}
            <main style={{ flex: 1, overflowY: 'auto', padding: '24px', backgroundColor: '#101629' }}>
                <Outlet />
            </main>
        </div>
    );
}
