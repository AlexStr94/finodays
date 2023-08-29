import { NavigationContainer } from "@react-navigation/native";
import { createNativeStackNavigator } from "@react-navigation/native-stack";
import Home from "./components/Home";
import Gosuslugi from "./components/Gosuslugi";
import Cards from "./components/Cards";
import { useReducer, createContext } from "react";
import Card from "./components/Card";

const Stack = createNativeStackNavigator();
export const MyContext = createContext();

const initialState = {
  isAuth: false,
  card_id: null,
  cards: [],
  card: {},
  token: {},
};

const reducer = (state, action) => {
  switch (action.type) {
    case "AUTH":
      return {
        ...state,
        isAuth: true,
        token: { ...action.payload },
      };
    case "SET_CARDS":
      return {
        ...state,
        cards: [...action.payload],
      };
    case "SET_CARD_ID":
      return {
        ...state,
        card_id: action.card_id,
      };
    case "SET_CARD":
      return {
        ...state,
        card: { ...action.payload },
      };
    default:
      return state;
  }
};

export default function App() {
  const [state, dispatch] = useReducer(reducer, initialState);

  return (
    <MyContext.Provider value={{ state, dispatch }}>
      <NavigationContainer>
        <Stack.Navigator initialRouteName="Home">
          <Stack.Screen
            name="Home"
            options={{ headerShown: false }}
            component={Home}
          />
          <Stack.Screen
            options={{ title: "Сайт гос услуг" }}
            name="Gosuslugi"
            component={Gosuslugi}
          />
          <Stack.Screen
            name="Cards"
            options={{ headerShown: false }}
            component={Cards}
          />
          <Stack.Screen
            name="Card"
            options={{ headerShown: false }}
            component={Card}
          />
        </Stack.Navigator>
      </NavigationContainer>
    </MyContext.Provider>
  );
}
