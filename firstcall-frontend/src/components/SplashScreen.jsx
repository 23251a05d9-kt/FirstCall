import { motion } from "framer-motion";

const SplashScreen = () => {
  return (
    <div className="min-h-screen flex items-center justify-center bg-[#050816]">
      <motion.div
        initial={{ opacity: 0, scale: 0.8 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 1 }}
        className="text-center"
      >
        <h1
          className="text-5xl tracking-widest text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-blue-400"
          style={{ fontFamily: "Orbitron, sans-serif" }}
        >
          FIRSTCALL
        </h1>

        <motion.div
          initial={{ width: 0 }}
          animate={{ width: "200px" }}
          transition={{ duration: 1.5 }}
          className="h-1 mt-4 mx-auto bg-gradient-to-r from-purple-500 to-blue-500 rounded-full"
        />
      </motion.div>
    </div>
  );
};

export default SplashScreen;
