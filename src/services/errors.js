export function errorMessage(error) {
    if (!error.response) return 'Não foi possível conectar ao servidor.';
    return Object.entries(error.response.data || {}).map(([key, value]) => `${key}: ${Array.isArray(value) ? value.join(' ') : value}`).join(' • ') || 'Operação não permitida.';
}

