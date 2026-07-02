import { Outlet } from 'react-router-dom';
import Sidebar from '../components/sidebar/index.jsx'; 

export default function App() {
    return (
        <div style={{ display: 'flex', height: '100vh', width: '100vw' }}>
            {/* SIDEBAR */}
            <Sidebar />

            {/* CONTENT */}
            <main style={{ flex: 1, overflowY: 'auto', padding: '24px', backgroundColor: '#f5f5f7' }}>
                <Outlet />
            </main>
        </div>
    );
}
