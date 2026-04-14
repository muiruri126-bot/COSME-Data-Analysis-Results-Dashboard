import app from './app';

const PORT = process.env.PORT || 3001;

app.listen(PORT, () => {
  console.log(`COSME Procurement Tracker API running on port ${PORT}`);
});

export default app;

