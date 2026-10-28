import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchRecipeById } from '../api/mockApi';
import Loader from '../components/Loader';
import './RecipePage.css';

const RecipePage = () => {
  const { id } = useParams();
  const [recipe, setRecipe] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchRecipeById(id).then((r) => {
      setRecipe(r || null);
      setLoading(false);
    });
  }, [id]);

  if (loading) return <Loader />;
  if (!recipe) return <p className="recipe-not-found">Рецепт не найден.</p>;

  return (
    <div className="recipe-page">
      <Link to="/recipes" className="recipe-back">← Назад к рецептам</Link>
      <h1 className="recipe-name">{recipe.name}</h1>
      <div className="recipe-meta">
        {recipe.cuisine} • {recipe.timeMinutes} мин • {recipe.difficulty}
      </div>

      <div className="recipe-block">
        <h2>Ингредиенты</h2>
        <ul>
          {recipe.ingredients.map((ing) => (
            <li key={ing}>{ing}</li>
          ))}
        </ul>
      </div>

      <div className="recipe-block">
        <h2>Приготовление</h2>
        <ol>
          {recipe.steps.map((step, i) => (
            <li key={i}>{step}</li>
          ))}
        </ol>
      </div>
    </div>
  );
};

export default RecipePage;
