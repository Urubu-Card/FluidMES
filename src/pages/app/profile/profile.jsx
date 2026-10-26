import { useOutletContext, Link } from "react-router-dom";
export default function Profile() {
  const user = useOutletContext();
  return (
    <section className="mes-page">
      <h1>Perfil</h1>
      <p>
        {user.first_name} {user.last_name}
      </p>
      <p>{user.email}</p>
      <p>{user.empresa?.nome}</p>
      <p>Cargo: {{ 1: "Preposto", 2: "Chefe", 3: "Funcionário" }[user.role]}</p>
      <Link to="/auth/forgot-password">Redefinir senha por e-mail</Link>
    </section>
  );
}
