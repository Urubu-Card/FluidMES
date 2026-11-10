import { useMemo } from "react";
import EntityForm from "../../shared/EntityForm";
import Modal from "../../shared/Modal";
import { DataState } from "../../shared/UI";
import useData from "../../shared/useData";

export default function SensorForm({ fields, ...props }) {
  const { data, error, loading, reload } = useData(["/api/sensores/unidades/"]);
  const unidades = data?.[0];
  const sensorFields = useMemo(() => fields.map((field) =>
    field.name === "unidade" ? { ...field, optionsBy: unidades } : field,
  ), [fields, unidades]);

  if (!unidades) {
    return (
      <Modal title={props.title} onClose={props.onClose}>
        <DataState loading={loading} error={error} reload={reload} />
      </Modal>
    );
  }
  return <EntityForm {...props} fields={sensorFields} />;
}
