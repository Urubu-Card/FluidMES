import { useState } from 'react';
import { Link, useSearchParams } from 'react-router-dom';
import api from '../../services/api';
import { errorMessage } from '../../services/errors';
export default function ResetPassword() {
    const [params] = useSearchParams();
    const [password,setPassword] = useState('');
    const [confirmation,setConfirmation] = useState('');
    const [message,setMessage] = useState('');
    const [busy,setBusy] = useState(false);
    async function submit(e) {
        e.preventDefault();
        if(password!==confirmation) return setMessage('As senhas não coincidem.');
        setBusy(true);
        try { await api.post('/api/password-reset/confirm/',{token:params.get('token'),nova_senha:password}); setMessage('Senha redefinida. Você já pode entrar.'); }
        catch(error) {setMessage(errorMessage(error));}
        finally {setBusy(false);}
    }
    return <main className="resource-page p-5"><h1>Redefinir senha</h1><form className="resource-form" onSubmit={submit}><label>Nova senha<input type="password" required minLength={8} value={password} onChange={e=>setPassword(e.target.value)}/></label><label>Confirmar senha<input type="password" required value={confirmation} onChange={e=>setConfirmation(e.target.value)}/></label><button disabled={busy || !params.get('token')}>Salvar senha</button></form><p role="status">{message}</p><Link to="/auth">Voltar ao login</Link></main>;
}
