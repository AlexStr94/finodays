import { Link } from "react-router-dom";
import style from "./Error.module.scss";
import qr from "../../assets/image.png";

const LoginError = () => {
  return (
    <div className={style.error}>
      <div className={style.error__info}>
        <h1>Подробная информация для подключения в системе:</h1>
        <img src={qr} alt="qr code image" />
      </div>
      <Link className={style.error__link} to={"/"}>
        На главный экран
      </Link>
    </div>
  );
};

export default LoginError;
