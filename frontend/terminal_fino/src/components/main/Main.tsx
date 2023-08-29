import { useNavigate } from "react-router-dom";
import style from "./Main.module.scss";
import { useRef, useState, useEffect, Dispatch, FC } from "react";
import { TypeAction } from "../..";

interface IMain {
  set: Dispatch<TypeAction>;
}

const Main: FC<IMain> = ({ set }) => {
  const [status, setStatus] = useState<"start" | "turning" | "identification">(
    "start"
  );
  const navigate = useNavigate();

  const video = useRef<HTMLVideoElement>(null);

  let stream: MediaStream | null = null;

  useEffect(() => {
    return () => {
      setStatus("start");
      if (stream) {
        stream.getTracks().forEach((track) => track.stop());
        stream = null;
      }
    };
  }, []);

  const handleStart = async () => {
    setStatus("turning");
    const constraints = {
      audio: false,
      video: { width: 320, height: 480, facingMode: "user" },
    };
    stream = await navigator.mediaDevices.getUserMedia(constraints);
    const videoStream = video.current;
    if (!videoStream) return;
    videoStream.srcObject = stream;
    videoStream.onloadedmetadata = () => {
      setStatus("identification");
      videoStream.play();
      const canvas = document.createElement("canvas");
      canvas.width = videoStream.videoWidth;
      canvas.height = videoStream.videoHeight;
      const context = canvas.getContext("2d");
      if (!context) return;
      context.drawImage(videoStream, 0, 0, canvas.width, canvas.height);
      canvas.toBlob((blob) => {
        if (!blob) return;
        const formData = new FormData();
        formData.append("file_in", blob);
        setTimeout(() => {
          fetch("http://80.78.241.76/api/v1/terminal", {
            method: "POST",
            body: formData,
          })
            .then((res) => res.json())
            .then((json) => {
              set({
                type: "SET",
                payload: json,
              });
              navigate("/payment");
            })
            .catch(() => alert("Упс ошибкаю Сейчас исправим"));
        }, 2000);
      }, "image/jpeg");
    };
  };

  return (
    <div className={style.main}>
      <video ref={video} className={style.main__web_camera} />
      <button
        disabled={status === "identification" || status === "turning"}
        onClick={handleStart}
        className={style.main__start}
      >
        {status === "start" && "Начать"}
        {status === "turning" && "Включения камеры..."}
        {status === "identification" && "Идентификация пользователя..."}
      </button>
    </div>
  );
};

export default Main;
