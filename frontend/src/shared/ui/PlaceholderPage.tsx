type PlaceholderPageProps = {
  title: string;
};

export function PlaceholderPage({ title }: PlaceholderPageProps) {
  return (
    <section className="placeholder-page">
      <p className="placeholder-page__eyebrow">Beatris</p>
      <h1>{title}</h1>
      <p>Экран подготовлен в структуре проекта и будет реализован следующим шагом.</p>
    </section>
  );
}
