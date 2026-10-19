import { useCallback, useEffect, useRef, useState } from "react";
import api from "../../../services/api";
import { useWorkspace } from "./context";
import { errorMessage } from "../../../services/errors";
export default function useData(paths, interval = 0) {
  const [data, setData] = useState(null);
  const [error, setError] = useState("");
  const { notify } = useWorkspace();
  const active = useRef(true);
  const pending = useRef(false);
  const key = JSON.stringify(paths);
  const reload = useCallback(async () => {
    if (pending.current) return;
    pending.current = true;
    try {
      const requestedPaths = JSON.parse(key);
      if (
        requestedPaths.some((path) =>
          /^\/api\/(pedidos|plantas|rendimentos|paradas)\//.test(path),
        )
      ) {
        await api.post("/api/simulacao/sincronizar/");
      }
      const responses = await Promise.all(
        requestedPaths.map((path) => api.get(path)),
      );
      if (active.current) {
        setData(responses.map((response) => response.data));
        setError("");
      }
    } catch (err) {
      if (active.current) setError(errorMessage(err));
    } finally {
      pending.current = false;
    }
  }, [key]);
  useEffect(() => {
    active.current = true;
    reload();
    const timer = interval
      ? setInterval(() => {
          if (!document.hidden) reload();
        }, interval)
      : null;
    return () => {
      active.current = false;
      clearInterval(timer);
    };
  }, [reload, interval]);
  const act = async (operation, message) => {
    try {
      const result = await operation();
      notify(message || result.data?.detail || "Alteração salva.");
      await reload();
      return true;
    } catch (err) {
      notify(errorMessage(err), "error");
      return false;
    }
  };
  return { data, error, reload, act, loading: !data && !error };
}
