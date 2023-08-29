import {
  View,
  StyleSheet,
  Text,
  TextInput,
  TouchableOpacity,
} from "react-native";
import { useEffect, useState, useContext } from "react";
import { MyContext } from "../App";

const Gosuslugi = ({ navigation }) => {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const { state, dispatch } = useContext(MyContext);

  useEffect(() => {
    state.isAuth && navigation.navigate("Cards");
  }, [state.isAuth]);

  const handleLogin = () => {
    function urlEncode(data) {
      return Object.entries(data)
        .map(
          ([key, value]) =>
            encodeURIComponent(key) + "=" + encodeURIComponent(value)
        )
        .join("&");
    }
    fetch("http://80.78.241.76/api/v1/auth", {
      method: "POST",
      headers: {
        "Content-Type": "application/x-www-form-urlencoded",
      },
      body: urlEncode({ username: email, password }),
    })
      .then((res) => res.json())
      .then((json) => {
        dispatch({
          type: "AUTH",
          payload: json,
        });
      })
      .catch((error) => console.log(error.message));
  };

  return (
    <View style={styles.conatiner}>
      <Text style={styles.title}>ГосУслуги</Text>
      <View style={styles.form}>
        <Text style={styles.label}>Логин:</Text>
        <TextInput
          style={styles.input}
          placeholder="Введите ваш email"
          value={email}
          onChangeText={setEmail}
        />
        <Text style={styles.label}>Пароль:</Text>
        <TextInput
          style={styles.input}
          secureTextEntry
          placeholder="Введите ваш пароль"
          value={password}
          onChangeText={setPassword}
        />
        <TouchableOpacity style={styles.button} onPress={handleLogin}>
          <Text style={styles.button_text}>Войти</Text>
        </TouchableOpacity>
      </View>
    </View>
  );
};

const styles = StyleSheet.create({
  conatiner: {
    flex: 1,
    justifyContent: "center",
    alignItems: "center",
    gap: 20,
  },

  input: {
    paddingHorizontal: 10,
    paddingVertical: 5,
    fontSize: 18,
    borderWidth: 1,
    borderColor: "black",
    marginBottom: 8,
  },

  form: {
    borderWidth: 2,
    borderColor: "black",
    borderRadius: 8,
    padding: 10,
  },

  title: {
    fontSize: 28,
    color: "black",
  },

  label: {
    marginBottom: 10,
    fontSize: 20,
  },

  button: {
    paddingVertical: 10,
    paddingHorizontal: 20,
    backgroundColor: "green",
    borderRadius: 10,
    fontSize: 18,
  },

  button_text: {
    color: "white",
    textAlign: "center",
  },
});

export default Gosuslugi;
