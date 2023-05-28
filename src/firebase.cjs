const admin = require('firebase-admin');

// Parse the credentials from the environment variable
const serviceAccount = JSON.parse(process.env.FIREBASE_CREDENTIALS);

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  storageBucket: "calculoidf.appspot.com"
});

const bucket = admin.storage().bucket();

async function uploadFile(filePath) {
  await bucket.upload(filePath, {
    gzip: true,
    metadata: {
      cacheControl: 'public, max-age=31536000',
    },
  });

  console.log(`${filePath} uploaded to Firebase Storage.`);
}

async function deleteFile(filePath) {
  await bucket.file(filePath).delete();

  console.log(`File ${filePath} deleted from Firebase Storage.`);
}

module.exports = { uploadFile, deleteFile };