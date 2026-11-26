import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchExhibitById, fetchRelated } from '../api/api';
import Loader from '../components/Loader';
import './ExhibitPage.css';

const ExhibitPage = () => {
  const { id } = useParams();
  const [exhibit, setExhibit] = useState(null);
  const [related, setRelated] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    setLoading(true);
    setError(null);
    Promise.all([fetchExhibitById(id), fetchRelated(id).catch(() => [])])
      .then(([e, rel]) => {
        setExhibit(e);
        setRelated(rel);
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false));
  }, [id]);

  if (loading) return <Loader />;
  if (error) {
    return error.startsWith('HTTP 404') ? (
      <p className="exhibit-not-found">Экспонат не найден.</p>
    ) : (
      <p className="error">Ошибка загрузки: {error}</p>
    );
  }

  return (
    <div className="exhibit-page">
      <Link to="/exhibits" className="exhibit-back">← Назад к экспонатам</Link>
      <h1 className="exhibit-name">{exhibit.name}</h1>
      <div className="exhibit-meta">
        {exhibit.author} • {exhibit.year} • {exhibit.style}
      </div>

      <div className="exhibit-block">
        <h2>Об экспонате</h2>
        <p>{exhibit.description}</p>
      </div>

      <div className="exhibit-block">
        <h2>Характеристики</h2>
        <ul>
          <li>Тип: {exhibit.type}</li>
          <li>Эпоха: {exhibit.epoch}</li>
          <li>Стиль: {exhibit.style}</li>
          <li>Темы: {exhibit.themes.join(', ')}</li>
          <li>Музей: {exhibit.museum}</li>
        </ul>
      </div>

      {related.length > 0 && (
        <div className="exhibit-block">
          <h2>Похожие экспонаты</h2>
          <ul className="related-list">
            {related.map((r) => (
              <li key={r.id}>
                <Link to={`/exhibits/${r.id}`}>{r.name}</Link>
                <span className="related-meta"> — {r.author}, {r.year}</span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
};

export default ExhibitPage;
