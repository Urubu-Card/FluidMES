import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../../../services/api'

function Home() {
    const [tasks, setTasks] = useState([])
    const [taskEdit, setTaskEdit] = useState(null)
    const [titulo, setTitulo] = useState('')
    const navigate = useNavigate()

    // Recupera o token salvo no localStorage
    const token = localStorage.getItem('@api:token')

    // GET - Listar as tarefas do usuário logado
    async function getTasks() {
        if (!token) {
            navigate('/auth')
            return
        }

        try {
            const response = await api.get('/api/tasks', {
                headers: { Authorization: `Bearer ${token}` }
            })
            setTasks(response.data)
        } catch (error) {
            console.error("Erro ao listar tarefas. O token pode ter expirado.", error)
            if (error.response?.status === 401) {
                handleLogout()
            }
        }
    }

    // POST - Adicionar nova tarefa
    async function createTask(e) {
        e.preventDefault()
        if (!titulo.trim()) return

        try {
            await api.post('/api/tasks', { titulo, concluida: false }, {
                headers: { Authorization: `Bearer ${token}` }
            })
            setTitulo('')
            getTasks()
        } catch (error) {
            console.error("Erro ao criar tarefa.", error)
        }
    }

    // PATCH - Modificar o conteúdo ou status da tarefa
    async function updateTask() {
        if (!taskEdit) return

        try {
            await api.patch(`/api/tasks/${taskEdit.id}`, {
                titulo: taskEdit.titulo,
                concluida: taskEdit.concluida
            }, {
                headers: { Authorization: `Bearer ${token}` }
            })
            setTaskEdit(null)
            getTasks()
        } catch (error) {
            console.error("Erro ao atualizar tarefa.", error)
        }
    }

    // DELETE - Apagar tarefa
    async function deleteTask(id) {
        const confirmDelete = window.confirm("Deseja mesmo remover esta tarefa?")
        if (!confirmDelete) return

        try {
            await api.delete(`/api/tasks/${id}`, {
                headers: { Authorization: `Bearer ${token}` }
            })
            getTasks()
        } catch (error) {
            console.error("Erro ao deletar tarefa.", error)
        }
    }

    // Função para limpar sessão (Logout)
    function handleLogout() {
        localStorage.removeItem('@api:token')
        navigate('/auth')
    }

    // Disparado ao montar o componente
    useEffect(() => {
        getTasks()
    }, [])

    // Trava scroll da tela quando modal de edição está aberto
    useEffect(() => {
        document.body.style.overflow = taskEdit ? "hidden" : "auto"
        return () => { document.body.style.overflow = "auto" }
    }, [taskEdit])

    return (
        <div className="container">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', width: '100%', maxWidth: '380px', marginBottom: '10px' }}>
                <span style={{ color: '#aaa', fontSize: '14px' }}>Sessão Ativa</span>
                <button onClick={handleLogout} style={{ background: '#ff4a4a', padding: '5px 12px', fontSize: '12px', width: 'auto' }}>Sair</button>
            </div>

            <form onSubmit={createTask}>
                <h1>Minhas Tarefas</h1>
                <div className="user-pass">
                    <input
                        type="text"
                        placeholder="Nome da Tarefa..."
                        required
                        value={titulo}
                        onChange={e => setTitulo(e.target.value)}
                    />
                    <i className="input-icon bx bx-task"></i>
                </div>
                <button type="submit">Adicionar</button>
            </form>

            {tasks.map(task => (
                <div key={task.id} className='card'>
                    <div>
                        <p>ID: <span>{task.id}</span></p>
                        <p>Tarefa: <span>{task.titulo}</span></p>
                        <p>Status: <span style={{ color: task.concluida ? '#4CAF50' : '#FFC107' }}>
                            {task.concluida ? 'Concluída ✅' : 'Pendente ⏳'}
                        </span></p>
                    </div>
                    <div className='actions'>
                        <span className='line'></span>
                        <div className='options'>
                            <button className='btn-edit' onClick={() => setTaskEdit({ id: task.id, titulo: task.titulo, concluida: task.concluida })}>
                                <i className='bx bx-pencil'></i>
                            </button>
                            <button className='btn-delete' onClick={() => deleteTask(task.id)}>
                                <i className="bx bx-trash"></i>
                            </button>
                        </div>
                    </div>
                </div>
            ))}

            {taskEdit && (
                <div className="bg-blur">
                    <div className="box-float">
                        <div className='header-edit'>
                            <h2>Editar Tarefa</h2>
                            <button className='close' onClick={() => setTaskEdit(null)}>
                                <i className='bx bx-x'></i>
                            </button>
                        </div>
                        <p>ID: <span>{taskEdit.id}</span></p>

                        <div className='box-edit'>
                            <div className="user-edit">
                                <p>Título: </p>
                                <input
                                    type="text"
                                    value={taskEdit.titulo}
                                    onChange={e => setTaskEdit({ ...taskEdit, titulo: e.target.value })}
                                />
                            </div>

                            <div className="user-edit" style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                                <p>Concluída: </p>
                                <input
                                    type="checkbox"
                                    checked={taskEdit.concluida}
                                    onChange={e => setTaskEdit({ ...taskEdit, concluida: e.target.checked })}
                                />
                            </div>

                            <button className='confirm-edit' onClick={updateTask}>
                                Salvar <i className='bx bxs-save'></i>
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    )
}

export default Home
