import { useEffect, useState } from 'react';
import { fetchExhibits } from '../api/api';
import ExhibitCard from '../components/ExhibitCard';
import Loader from '../components/Loader';
import './ExhibitsPage.css';

const ExhibitsPage = () => {
  const [exhibits, setExhibits] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [filter, setFilter] = useState('');

  useEffect(() => {
    fetchExhibits()
      .then(setExhibits)
      .catch((e) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  const q = filter.toLowerCase();
  const filtered = exhibits.filter(
    (e) =>
      e.name.toLowerCase().includes(q) ||
      e.author.toLowerCase().includes(q) ||
      e.style.toLowerCase().includes(q) ||
      e.epoch.toLowerCase().includes(q) ||
      e.themes.some((t) => t.toLowerCase().includes(q))
  );

  if (loading) return <Loader />;
  if (error) return <p className="error">Ошибка загрузки: {error}</p>;

  return (
    <div className="exhibits">
      <h1 className="exhibits-title">🖼️ Экспонаты</h1>
      <input
        type="text"
        className="exhibits-search"
        placeholder="Поиск по названию, автору, эпохе, стилю или теме..."
        value={filter}
        onChange={(e) => setFilter(e.target.value)}
      />
      {filtered.length === 0 ? (
        <p className="exhibits-empty">Ничего не найдено.</p>
      ) : (
        <div className="exhibits-grid">
          {filtered.map((e) => (
            <ExhibitCard key={e.id} exhibit={e} />
          ))}
        </div>
      )}
    </div>
  );
};

export default ExhibitsPage;
