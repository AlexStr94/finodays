import { Dispatch, FC, useEffect } from "react";
import { Link, useNavigate } from "react-router-dom";
import style from "./End.module.scss";
import { TypeAction } from "../..";

interface IEnd {
  set: Dispatch<TypeAction>;
}

const End: FC<IEnd> = ({ set }) => {
  const navigate = useNavigate();

  useEffect(() => {
    setTimeout(() => navigate("/", { replace: true }), 2000);

    return () => set({ type: "SET", payload: {} });
  }, []);

  return (
    <div className={style.end}>
      <h1>Спасибо за оплату!</h1>
      <Link to={"/"}>
        <svg
          width="100px"
          height="100px"
          viewBox="0 0 64 64"
          xmlns="http://www.w3.org/2000/svg"
          xmlnsXlink="http://www.w3.org/1999/xlink"
          aria-hidden="true"
          role="img"
          preserveAspectRatio="xMidYMid meet"
        >
          <circle cx="32" cy="32" r="30" fill="#4bd37b"></circle>
          <path
            fill="#ffffff"
            d="M46 14L25 35.6l-7-7.2l-7 7.2L25 50l28-28.8z"
          ></path>
        </svg>
      </Link>
    </div>
  );
};

export default End;
