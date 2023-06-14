const admin = require('firebase-admin');
require('dotenv').config();

// Parse the credentials from the environment variable
const serviceAccount = JSON.parse(Buffer.from(process.env.FIREBASE_CREDENTIALS, 'base64').toString());

admin.initializeApp({
  credential: admin.credential.cert(serviceAccount),
  storageBucket: "calculoidf.appspot.com"
});

const bucket = admin.storage().bucket();

async function uploadFile(filePath) {
  try {
    await bucket.upload(filePath, {
      gzip: true,
      metadata: {
        cacheControl: 'public, max-age=31536000',
      },
    });

    console.log(`${filePath} uploaded to Firebase Storage.`);
  } catch (error) {
    console.error(`Error uploading file to Firebase Storage: ${error}`);
    throw error;
  }
}

async function deleteFile(filePath) {
  try {
    await bucket.file(filePath).delete();

    console.log(`File ${filePath} deleted from Firebase Storage.`);
  } catch (error) {
    console.error(`Error deleting file from Firebase Storage: ${error}`);
    throw error;
  }
}

module.exports = { uploadFile, deleteFile, bucket };
