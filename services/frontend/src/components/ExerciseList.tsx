import { useState, useMemo } from 'react';
import type { Exercise, FilterType } from '../types/exercise';
import { exportExercisesCSV } from '../api/client';

const COLUMN_HEADERS: { key: keyof Exercise; label: string }[] = [
  { key: 'id', label: 'ID' },
  { key: 'name', label: 'Exercise' },
  { key: 'sets', label: 'Sets' },
  { key: 'reps', label: 'Reps' },
  { key: 'weight', label: 'Weight' },
  { key: 'workout_day', label: 'Day' },
];

const PAGE_SIZE = 10;

interface ExerciseListProps {
  exercises: Exercise[];
  onEdit: (exercise: Exercise) => void;
  onDelete: (exerciseId: number) => void;
}

export function ExerciseList({ exercises, onEdit, onDelete }: ExerciseListProps) {
  const [filterType, setFilterType] = useState<FilterType>('All');
  const [searchTerm, setSearchTerm] = useState('');
  const [workoutDayFilter, setWorkoutDayFilter] = useState<string>('All');
  const [sortColumn, setSortColumn] = useState<keyof Exercise | null>(null);
  const [sortDirection, setSortDirection] = useState<'desc' | 'asc'>('desc');
  const [currentPage, setCurrentPage] = useState(1);

  const filteredExercises = useMemo(() => {
    let result = exercises;
    if (filterType === 'Weighted Only') {
      result = result.filter((ex) => ex.weight !== null);
    } else if (filterType === 'Bodyweight Only') {
      result = result.filter((ex) => ex.weight === null);
    }
    if (workoutDayFilter !== 'All') {
      result = result.filter((ex) => ex.workout_day === workoutDayFilter);
    }
    if (searchTerm) {
      result = result.filter((ex) =>
        ex.name.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }
    return result;
  }, [exercises, filterType, workoutDayFilter, searchTerm]);

  const sortedExercises = useMemo(() => {
    if (!sortColumn) return filteredExercises;
    return [...filteredExercises].sort((a, b) => {
      const valA = a[sortColumn];
      const valB = b[sortColumn];
      if (valA === null && valB === null) return 0;
      if (valA === null) return 1;
      if (valB === null) return -1;
      const cmp =
        typeof valA === 'string' && typeof valB === 'string'
          ? valA.localeCompare(valB)
          : (valA as number) - (valB as number);
      return sortDirection === 'desc' ? -cmp : cmp;
    });
  }, [filteredExercises, sortColumn, sortDirection]);

  const totalPages = Math.max(1, Math.ceil(sortedExercises.length / PAGE_SIZE));
  const safePage = Math.min(currentPage, totalPages);
  const paginatedExercises = sortedExercises.slice(
    (safePage - 1) * PAGE_SIZE,
    safePage * PAGE_SIZE
  );

  const handleSort = (column: keyof Exercise) => {
    if (sortColumn === column) {
      setSortDirection((prev) => (prev === 'desc' ? 'asc' : 'desc'));
    } else {
      setSortColumn(column);
      setSortDirection('desc');
    }
    setCurrentPage(1);
  };

  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-text-primary mb-4">Exercise List</h3>

      {/* Filters */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-3 mb-4">
        <div>
          <label htmlFor="filter-type" className="block text-xs font-medium text-text-secondary mb-1">Type</label>
          <select
            id="filter-type"
            value={filterType}
            onChange={(e) => { setFilterType(e.target.value as FilterType); setCurrentPage(1); }}
            className="input"
          >
            <option value="All">All</option>
            <option value="Weighted Only">Weighted Only</option>
            <option value="Bodyweight Only">Bodyweight Only</option>
          </select>
        </div>
        <div>
          <label htmlFor="filter-workout-day" className="block text-xs font-medium text-text-secondary mb-1">Day</label>
          <select
            id="filter-workout-day"
            value={workoutDayFilter}
            onChange={(e) => { setWorkoutDayFilter(e.target.value); setCurrentPage(1); }}
            className="input"
          >
            <option value="All">All Days</option>
            <option value="None">Daily</option>
            <option value="A">Day A</option>
            <option value="B">Day B</option>
            <option value="C">Day C</option>
            <option value="D">Day D</option>
            <option value="E">Day E</option>
            <option value="F">Day F</option>
            <option value="G">Day G</option>
          </select>
        </div>
        <div>
          <label htmlFor="search" className="block text-xs font-medium text-text-secondary mb-1">Search</label>
          <input
            id="search"
            type="text"
            placeholder="Exercise name..."
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setCurrentPage(1); }}
            className="input"
          />
        </div>
      </div>

      {/* Info row */}
      <div className="flex items-center justify-between mb-3">
        <p className="text-xs text-text-muted">
          Showing {paginatedExercises.length} of {filteredExercises.length} exercises
          {filteredExercises.length !== exercises.length && ` (${exercises.length} total)`}
        </p>
        <button className="btn btn-secondary btn-sm" onClick={exportExercisesCSV}>
          Export CSV
        </button>
      </div>

      {filteredExercises.length > 0 ? (
        <>
          {/* Sort controls (desktop) */}
          <div className="hidden lg:flex items-center gap-2 mb-3">
            <span className="text-xs text-text-muted">Sort by:</span>
            {COLUMN_HEADERS.map(({ key, label }) => (
              <button
                key={key}
                className={`text-xs px-2.5 py-1 rounded-md transition-colors ${
                  sortColumn === key
                    ? 'bg-primary-muted text-primary font-medium'
                    : 'text-text-muted hover:text-text-secondary hover:bg-surface-light'
                }`}
                onClick={() => handleSort(key)}
              >
                {label}
                {sortColumn === key && (
                  <span className="ml-0.5">{sortDirection === 'desc' ? '\u2193' : '\u2191'}</span>
                )}
              </button>
            ))}
          </div>

          {/* Exercise cards */}
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-3">
            {paginatedExercises.map((exercise) => (
              <div key={exercise.id} className="bg-surface-light border-[1.5px] border-border rounded-2xl p-4 hover:border-border-light transition-colors">
                <div className="flex items-start justify-between mb-3">
                  <div>
                    <p className="text-base font-semibold text-text-primary">{exercise.name}</p>
                    <p className="text-xs text-text-muted mt-0.5">ID: {exercise.id}</p>
                  </div>
                  <span className="inline-block px-2.5 py-1 rounded-full text-xs font-medium bg-primary-muted text-primary">
                    {exercise.workout_day === 'None' ? 'Daily' : `Day ${exercise.workout_day}`}
                  </span>
                </div>
                <div className="flex items-center gap-3 mb-4">
                  <div className="flex-1 bg-surface border border-border/60 rounded-xl px-3 py-2 text-center">
                    <div className="text-sm font-bold text-text-primary">{exercise.sets}</div>
                    <div className="text-[10px] text-text-muted">Sets</div>
                  </div>
                  <div className="flex-1 bg-surface border border-border/60 rounded-xl px-3 py-2 text-center">
                    <div className="text-sm font-bold text-text-primary">{exercise.reps}</div>
                    <div className="text-[10px] text-text-muted">Reps</div>
                  </div>
                  <div className="flex-1 bg-surface border border-border/60 rounded-xl px-3 py-2 text-center">
                    <div className="text-sm font-bold text-text-primary">
                      {exercise.weight !== null ? `${exercise.weight}` : 'BW'}
                    </div>
                    <div className="text-[10px] text-text-muted">{exercise.weight !== null ? 'kg' : 'Bodyweight'}</div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  <button className="btn btn-edit btn-sm flex-1" onClick={() => onEdit(exercise)}>Edit</button>
                  <button
                    className="btn btn-danger btn-sm flex-1"
                    onClick={() => { if (window.confirm(`Delete "${exercise.name}"?`)) onDelete(exercise.id); }}
                  >
                    Delete
                  </button>
                </div>
              </div>
            ))}
          </div>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-center gap-2 mt-4 pt-4 border-t border-border">
              <button className="btn btn-secondary btn-sm" disabled={safePage === 1} onClick={() => setCurrentPage(1)}>
                &laquo;
              </button>
              <button className="btn btn-secondary btn-sm" disabled={safePage === 1} onClick={() => setCurrentPage((p) => p - 1)}>
                &lsaquo;
              </button>
              <span className="text-xs text-text-secondary px-2">
                Page {safePage} of {totalPages}
              </span>
              <button className="btn btn-secondary btn-sm" disabled={safePage === totalPages} onClick={() => setCurrentPage((p) => p + 1)}>
                &rsaquo;
              </button>
              <button className="btn btn-secondary btn-sm" disabled={safePage === totalPages} onClick={() => setCurrentPage(totalPages)}>
                &raquo;
              </button>
            </div>
          )}
        </>
      ) : (
        <div className="text-center py-8 text-text-muted text-sm">
          No exercises match your filters.
        </div>
      )}
    </div>
  );
}
