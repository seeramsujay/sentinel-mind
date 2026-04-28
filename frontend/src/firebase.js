import { initializeApp } from 'firebase/app';
import { getFirestore } from 'firebase/firestore';

const firebaseConfig = {
  projectId: import.meta.env.VITE_GCP_PROJECT_ID,
};

const app = initializeApp(firebaseConfig);
export const db = getFirestore(app);
